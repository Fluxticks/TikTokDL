import inspect
from asyncio import sleep as async_sleep
from datetime import datetime
from os.path import curdir
from os.path import sep as PATH_SEP
from urllib.request import urlretrieve

from playwright.async_api import Page, async_playwright

from tiktokdl.captcha import handle_captcha
from tiktokdl.exceptions import (
    CaptchaFailedException,
    DownloadFailedException,
    ResponseParseException,
    RetryLimitReached,
)
from tiktokdl.post_data import TikTokPost, TikTokSlide, TikTokVideo

from typing import Union

__all__ = ["get_post"]


def __filter_kwargs(function: callable, all_kwargs: dict):
    all_args = inspect.getfullargspec(function)
    allowed_args = all_args.kwonlyargs

    valid_kwargs = {}
    for key, value in all_kwargs.items():
        if key in allowed_args:
            valid_kwargs[key] = value

    return valid_kwargs


def __validate_download_path(download_path: Union[str, None]):
    if download_path is None:
        download_path = f"{curdir}{PATH_SEP}"

    if not download_path.endswith(PATH_SEP):
        download_path += PATH_SEP

    return download_path


def __post_is_slideshow(data: dict) -> bool:
    return data.get("imagePost") is not None


def __parse_api_response(
        api_response: dict) -> Union[TikTokSlide, TikTokVideo]:
    root_data = api_response.get("itemInfo").get("itemStruct")

    author_data = root_data.get("author")
    stats_data = root_data.get("stats")

    video_id = root_data.get("id")
    author_id = author_data.get("uniqueId")
    timestamp = datetime.fromtimestamp(int(root_data.get("createTime")))

    post = TikTokPost(
        url=f"https://tiktok.com/@{author_id}/video/{video_id}",
        post_id=video_id,
        post_description=root_data.get("desc"),
        timestamp=timestamp,
        author_username=author_id,
        author_display_name=author_data.get("nickname"),
        author_avatar=author_data.get("avatarLarger"),
        author_url=f"https://tiktok.com/@{author_id}",
        post_download_setting=author_data.get("downloadSetting"),
        like_count=stats_data.get("diggCount"),
        share_count=stats_data.get("shareCount"),
        comment_count=stats_data.get("commentCount"),
        view_count=stats_data.get("playCount"),
    )

    if __post_is_slideshow(root_data):
        images = root_data.get("imagePost").get("images")
        return TikTokSlide(**post.__dict__, images=images)
    else:
        video_thumbnail = root_data.get("video").get("originCover")
        return TikTokVideo(**post.__dict__, video_thumbnail=video_thumbnail)


async def download_video(playwright_page: Page, video_info: TikTokVideo,
                         timeout: float, download_path: Union[str, None]):
    """Uses the the browser request for the video to download the video. Valid for any download setting but less reliable.

    Args:
        playwright_page (Page): The current page.
        video_info (TikTokVideo): The video data of the TikTok video.
        timeout (float): THe number of ms to wait for the request to occur before timing out.
        download_path (str | None): The path to download the video to. If None, uses current directory.
    """
    download_path = __validate_download_path(download_path)
    page_video_tag = playwright_page.locator("video").first
    video_source = await page_video_tag.get_attribute("src")

    response_base_url = video_source.split("?")[0]
    async with playwright_page.expect_request_finished(
            lambda x: response_base_url in x.url, timeout=timeout) as request:
        request_value = await request.value
        response = await request_value.response()
        save_path = f"{download_path}{video_info.post_id}.mp4"
        with open(save_path, "wb") as f:
            f.write(await response.body())
        video_info.file_path = save_path


async def download_slideshow(video_info: TikTokSlide,
                             download_path: Union[str, None]):
    """For a given Slideshow post, download the images associated with it.

    Args:
        video_info (TikTokSlide): The Slideshow post data.
        download_path (str | None): The path to download the images to. If None, uses current directory.
    """
    download_path = __validate_download_path(download_path)

    images = []
    for idx, image_info in enumerate(video_info.images):
        image_url = image_info.get("imageURL").get("urlList")[-1]
        file = f"{download_path}{idx+1}.jpeg"
        urlretrieve(image_url, file)
        images.append(file)

    video_info.images = images


async def __get_post(url: str,
                     download: bool = True,
                     proxy: Union[dict, None] = None,
                     request_timeout: float = 5000,
                     download_path: Union[str, None] = None,
                     headless: Union[bool, None] = None,
                     slow_mo: Union[float, None] = None,
                     **kwargs) -> Union[TikTokSlide, TikTokVideo]:
    async with async_playwright() as playwright:
        # TODO: Find a way to use Chromium and be able to recive the download_video response body
        # browser = await playwright.chromium.launch(headless=headless, slow_mo=slow_mo, args=["--disable-http2"])
        other_kwargs = __filter_kwargs(playwright.firefox.launch, kwargs)
        browser = await playwright.firefox.launch(headless=headless,
                                                  slow_mo=slow_mo,
                                                  proxy=proxy,
                                                  **other_kwargs)
        device = playwright.devices["iPhone 14 Pro Max"]
        device.pop("is_mobile")
        context = await browser.new_context(**device)
        await context.clear_cookies()

        page = await context.new_page()
        await page.goto(url)
        if not await handle_captcha(page):
            raise CaptchaFailedException(url=url)

        async with page.expect_request(lambda x: "/api/item/detail/" in x.url,
                                       timeout=request_timeout) as request:
            await page.reload()
            request_value = await request.value
            response = await request_value.response()
            data = await response.json()
            try:
                parsed_response = __parse_api_response(data)
            except:
                raise ResponseParseException(url=url)

            if download:
                try:
                    if isinstance(parsed_response, TikTokSlide):
                        await download_slideshow(parsed_response,
                                                 download_path)
                    else:
                        await download_video(page, parsed_response,
                                             request_timeout, download_path)
                except:
                    raise DownloadFailedException(url=url)

        return parsed_response


async def get_post(url: str,
                   download: bool = True,
                   proxy: Union[dict, None] = None,
                   retries: int = 3,
                   retry_delay: float = 500,
                   request_timeout: float = 5000,
                   download_path: Union[str, None] = None,
                   headless: Union[bool, None] = None,
                   slow_mo: Union[float, None] = None,
                   **kwargs) -> Union[TikTokSlide, TikTokVideo]:
    """Get the information about a given video URL. If the `download` param is set to True, also download the video as an mp4 file or slideshow images as JPEG files.

    Args:
        url (str): The URL to get the information of.
        download (bool, optional): If the video should be downloaded locally. Defaults to True.
        proxy (dict | None, optional): The proxy settings to use for the request. Defaults to None.
        retries (int, optional): The number of times to retry upon failure. Defaults to 3.
        retry_delay (float, optional): The number of ms to wait before retrying. Defaults to 500.
        download_timeout (float, optional): The number of ms the download will wait to start before timing out.
        download_path (str | None, optional): The path to download vidoes or images to. Defaults to None, the current directory.
        headless (bool | None, optional): If the browser should be headless. Defaults to None.
        slow_mo (float | None, optional): Slow the browser down, useful when not headless. Defaults to None.

    Raises:
        ResponseParseException: If there was an error while parsing the response data to video info.
        CaptchaFailedException: If the captcha was not able to be solved.
        DownloadFailedException: If the video could not be downloaded.

    Returns:
        TikTokVideo | TikTokSlide: The data for the given URL as a TikTokVideo or TikTokSlide dataclass.
    """

    for x in range(retries + 1):
        try:
            result = await __get_post(url=url,
                                      download=download,
                                      proxy=proxy,
                                      request_timeout=request_timeout,
                                      download_path=download_path,
                                      headless=headless,
                                      slow_mo=slow_mo,
                                      **kwargs)
            return result
        except Exception as e:
            if x < retries:
                await async_sleep(retry_delay / 1000.0)
                continue

            raise RetryLimitReached(e, retries, url)
