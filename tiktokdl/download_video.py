import json
from datetime import datetime
import random
import time
from typing import Literal
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page, Request, BrowserContext
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from tiktokdl.exceptions import CaptchaFailedException, DownloadFailedException
from tiktokdl.image_processing import find_position, image_from_url
from tiktokdl.video_data import TikTokVideo

__all__ = ["get_video"]


def __parse_captcha_params_from_url(url: str) -> dict:
    parsed_url = urlparse(url, allow_fragments=False)
    params = parse_qs(parsed_url.query)
    out = {}
    for key, value in params.items():
        out[key] = value[0]
    return out


def __get_captcha_response_params(url: str) -> dict:
    request_params = __parse_captcha_params_from_url(url)
    request_params["tmp"] = f"{time.time()}{random.randint(111, 999)}"
    return request_params


async def __get_captcha_response_headers(request: Request) -> dict:
    all_headers = await request.all_headers()
    all_headers["content-type"] = "application/json;charset=UTF-8"
    return all_headers


def __parse_video_info(page_source: str) -> TikTokVideo:
    soup = BeautifulSoup(page_source, "lxml")
    script_data = soup.find("script", attrs={"id": "SIGI_STATE"})
    data = json.loads(script_data.text)

    post_url = data.get("SEOState").get("canonical")

    author_data = list(data.get("UserModule").get("users").values())[0]
    username = author_data.get("uniqueId")
    display_name = author_data.get("nickname")
    avatar = author_data.get("avatarThumb")
    author_url = f"https://www.tiktok.com/@{username}/"

    video_data = list(data.get("ItemModule").values())[0]
    video_description = video_data.get("desc")
    video_download_setting = video_data.get("downloadSetting")
    video_id = video_data.get("id")
    timestamp = datetime.fromtimestamp(int(video_data.get("createTime")))
    like_count = video_data.get("stats").get("diggCount")
    share_count = video_data.get("stats").get("shareCount")
    comment_count = video_data.get("stats").get("commentCount")
    view_count = video_data.get("stats").get("playCount")
    video_thumbnail = video_data.get("video").get("originCover")

    return TikTokVideo(
        url=post_url,
        video_id=video_id,
        author_username=username,
        author_display_name=display_name,
        author_avatar=avatar,
        author_url=author_url,
        video_download_setting=video_download_setting,
        video_description=video_description,
        timestamp=timestamp,
        like_count=like_count,
        share_count=share_count,
        comment_count=comment_count,
        view_count=view_count,
        video_thumbnail=video_thumbnail,
    )


def __generate_random_captcha_steps(piece_position: tuple[int, int], tip_y_value: int):
    x_position = piece_position[0]

    steps = []
    current_distance = 0
    relative_time = random.randint(100, 300)
    while current_distance < x_position:
        current_distance += random.randint(1, 4)
        relative_time += random.randint(6, 9)
        steps.append({"relative_time": relative_time, "x": current_distance, "y": tip_y_value})

    if steps[-1].get("x") < x_position or steps[-1].get("x") > x_position:
        steps.append({"relative_time": relative_time + random.randint(6, 9), "x": x_position, "y": tip_y_value})

    return steps


def __calculate_captcha_solution(captcha_get_data: dict) -> dict:
    data = captcha_get_data.get("data").get("question")

    bg_url = data.get("url1")
    piece_url = data.get("url2")
    tip_value = data.get("tip_y")

    bg_image = image_from_url(bg_url)
    piece_image = image_from_url(piece_url)

    position = find_position(bg_image, piece_image)

    body = {
        "modified_img_width": 552,
        "id": captcha_get_data.get("data").get("id"),
        "mode": "slide",
        "reply": __generate_random_captcha_steps(position,
                                                 tip_value)
    }

    return body


async def __handle_captcha(playwright_page: Page, retries: int = 3) -> bool:
    captcha_success_status = False
    retry_count = 0

    while not captcha_success_status and retry_count < retries:
        try:
            async with playwright_page.expect_request(lambda x: "/captcha/get?" in x.url) as request:
                await playwright_page.wait_for_load_state("networkidle")
                request_value = await request.value
                response = await request_value.response()
                response_data = await response.json()

                captcha_solution = __calculate_captcha_solution(response_data)
                post_url_query_params = __get_captcha_response_params(request_value.url)
                post_headers = await __get_captcha_response_headers(request_value)
                base_url = urlparse(request_value.url).netloc
                api_request_context = playwright_page.request

                await playwright_page.wait_for_timeout(1000)
                captcha_status = await api_request_context.post(
                    f"https://{base_url}/captcha/verify",
                    data=captcha_solution,
                    headers=post_headers,
                    params=post_url_query_params
                )

                if captcha_status.status != 200:
                    return False

                captcha_status_data = await captcha_status.json()
                captcha_success_status = captcha_status_data.get("message") == "Verification complete"
                retry_count += 1
                await playwright_page.locator("#verify-bar-close").click()

        except PlaywrightTimeoutError:
            return True
        except PlaywrightError:
            return False

    return captcha_success_status


async def __random_timeout_duration(playwright_page: Page, min_timeout: int, max_timout: int):
    timout_value = random.randint(min_timeout, max_timout)
    await playwright_page.wait_for_timeout(timout_value)


async def __close_popups(playwright_page: Page) -> int:
    close_buttons = await playwright_page.get_by_label("Close").all()
    for button in close_buttons:
        await button.click()

    await playwright_page.get_by_role("button", name="Decline all").click()
    await __random_timeout_duration(playwright_page, 500, 900)
    return len(close_buttons) + 1


async def get_video(
    url: str,
    download: bool = True,
    download_timeout: float = 5000,
    browser: Literal["firefox",
                     "chromium",
                     "chrome",
                     "safari",
                     "webkit"] = "firefox",
    headless: bool | None = None,
    slow_mo: float | None = None
) -> TikTokVideo:
    """Get the information about a given video URL. If the `download` param is set to True, also download the video as an mp4 file.

    Args:
        url (str): The URL to get the information of.
        download (bool, optional): If the video should be downloaded locally. Defaults to True.
        download_timeout (float, optional): The number of ms the download will wait to start before timing out.
        browser (Literal[&quot;firefox&quot;, &quot;chromium&quot;, &quot;chrome&quot;, &quot;safari&quot;, &quot;webkit&quot;], optional): The browser to use to scrape the content. Defaults to "firefox".
        headless (bool | None, optional): If the browser should be headless. Defaults to None.
        slow_mo (float | None, optional): Slow the browser down, useful when not headless. Defaults to None.

    Raises:
        TypeError: If the given browser is not a valid browser.
        CaptchaFailedException: If the captcha was not able to be solved.
        DownloadFailedException: If the video could not be downloaded.

    Returns:
        TikTokVideo: The data for the given URL as a TikTokVideo dataclass.
    """
    async with async_playwright() as playwright:
        match browser:
            case "firefox":
                browser_instance = playwright.firefox
            case "chrome":
                browser_instance = playwright.chromium
            case "chromium":
                browser_instance = playwright.chromium
            case "safari":
                browser_instance = playwright.webkit
            case "webkit":
                browser_instance = playwright.webkit
            case _:
                raise TypeError(f"Invalid browser given. Browser {browser} is not valid.")

        browser_instance = await browser_instance.launch(headless=headless, slow_mo=slow_mo)
        browser_context = await browser_instance.new_context()
        await browser_context.clear_cookies()

        video_page = await browser_context.new_page()
        await video_page.goto(url)

        page_source = await video_page.content()
        video_info = __parse_video_info(page_source)
        if not download:
            return video_info

        captcha_success_result = await __handle_captcha(video_page)
        if not captcha_success_result:
            raise CaptchaFailedException(url)

        await __close_popups(video_page)

        try:
            if video_info.video_download_setting == 0:
                await primary_download_strategy(browser_context, video_page, video_info, download_timeout)
            else:
                await alternate_download_strategy(video_page, video_info, download_timeout)
        except PlaywrightTimeoutError:
            raise DownloadFailedException(url=url)

        return video_info


async def primary_download_strategy(
    browser_context: BrowserContext,
    playwright_page: Page,
    video_info: TikTokVideo,
    timeout: float
):
    """Downloads the TikTok video using the UI download button that appears on a video. Only valid for videos with download setting 0.

    Args:
        browser_context (BrowserContext): The current browser context.
        playwright_page (Page): The current page.
        video_info (TikTokVideo): The video data of the TikTok video.
        timeout (float): The number of ms to wait for the download to start before timing out.
    """
    browser_context.set_default_timeout(timeout)
    page_video_tag = playwright_page.locator("video").first
    await page_video_tag.click(button="right")
    await __random_timeout_duration(playwright_page, 100, 500)
    download_video_li = playwright_page.locator("li", has_text="Download video")
    async with playwright_page.expect_download() as download_info:
        await download_video_li.click()
        download = await download_info.value
        save_path = f"{video_info.video_id}.mp4"
        await download.save_as(save_path)
        video_info.file_path = save_path


async def alternate_download_strategy(playwright_page: Page, video_info: TikTokVideo, timeout: float):
    """Uses the the browser request for the video to download the video. Valid for any download setting but less reliable.

    Args:
        playwright_page (Page): The current page.
        video_info (TikTokVideo): The video data of the TikTok video.
        timeout (float): THe number of ms to wait for the request to occur before timing out.
    """
    page_video_tag = playwright_page.locator("video").first
    video_source = await page_video_tag.get_attribute("src")

    response_base_url = video_source.split("?")[0]
    async with playwright_page.expect_response(lambda x: response_base_url in x.url, timeout=timeout) as response_info:
        await playwright_page.reload()
        response = await response_info.value
        save_path = f"{video_info.video_id}.mp4"
        with open(save_path, "wb") as f:
            f.write(await response.body())
        video_info.file_path = save_path
