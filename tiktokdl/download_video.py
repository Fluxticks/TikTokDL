from random import random
from time import time
from typing import Literal
from urllib.parse import parse_qs, urlparse

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page, Request
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from tiktokdl.exceptions import CaptchaFailedException, DownloadFailedException
from tiktokdl.image_processing import find_position, image_from_url
from tiktokdl.video_data import TikTokVideo

__all__ = ["download"]


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
    pass


def __generate_random_captcha_steps(piece_position: tuple[int, int], tip_y_value: int):
    pass


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
    browser: Literal["firefox",
                     "chromium",
                     "chrome",
                     "safari",
                     "webkit"] = "firefox",
    headless: bool | None = None,
    slow_mo: float | None = None
) -> TikTokVideo:
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

        page_video_tag = video_page.locator("video").first
        await page_video_tag.click(button="right")
        await __random_timeout_duration(video_page, 100, 500)
        download_video_li = video_page.locator("li", has_text="Download video")
        try:
            async with video_page.expect_download() as download_info:
                await download_video_li.click()
                download = await download_info.value
                save_path = f"{video_info.video_id}.mp4"
                await download.save_as(save_path)
                video_info.file_path = save_path
        except PlaywrightTimeoutError:
            raise DownloadFailedException(url=url)

        return video_info