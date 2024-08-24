import inspect
from asyncio import sleep as async_sleep
from datetime import datetime, timezone
from os.path import curdir
from os.path import sep as PATH_SEP
from urllib.parse import urlparse
import requests
from urllib.request import urlretrieve

from playwright.async_api import BrowserContext, async_playwright, Playwright

from tiktokdl.exceptions import (
    DownloadFailedException,
    ResponseParseException,
    RetryLimitReached,
)
from tiktokdl.post_data import TikTokPost, TikTokSlide, TikTokVideo

from typing import Literal, Union

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
    return data.get("image") is not None


def __parse_api_response(api_response: dict) -> Union[TikTokSlide, TikTokVideo]:
    root_data = api_response.get("item_info")

    stats_data = root_data.get("item_stats")
    post_data = root_data.get("item_basic")
    author_data = post_data.get("creator").get("base")

    video_id = post_data.get("id")
    author_username = author_data.get("unique_id")
    author_id = author_data.get("id")
    timestamp = datetime.fromtimestamp(
        int(post_data.get("create_time")), tz=timezone.utc
    )

    post = TikTokPost(
        url=f"https://tiktok.com/@{author_id}/video/{video_id}",
        post_id=video_id,
        post_description=post_data.get("desc"),
        timestamp=timestamp,
        author_username=author_username,
        author_id=author_id,
        author_display_name=author_data.get("nick_name"),
        author_avatar=author_data.get("avatar_larger")[-1],
        author_url=f"https://tiktok.com/@{author_username}",
        post_download_setting=-1,
        like_count=stats_data.get("digg_count"),
        share_count=stats_data.get("share_count"),
        comment_count=stats_data.get("comment_count"),
        view_count=stats_data.get("play_count"),
    )

    if __post_is_slideshow(post_data):
        images = post_data.get("image").get("images")
        return TikTokSlide(**post.__dict__, images=images)
    else:
        video_thumbnail = (
            post_data.get("video").get("video_cover").get("origin_cover")[0]
        )
        download_url = (
            post_data.get("video").get("video_play_info").get("download_addr")[0]
        )
        return TikTokVideo(
            **post.__dict__, video_thumbnail=video_thumbnail, download_url=download_url
        )


async def __get_browser(
    playwright_instance: Playwright,
    browser: str,
    proxy: Union[dict, None] = None,
    headless: Union[bool, None] = None,
    slow_mo: Union[float, None] = None,
    **kwargs,
) -> BrowserContext:

    browser_instance = None

    if browser == "chromium":
        filtered_args = __filter_kwargs(playwright_instance.chromium.launch, kwargs)
        browser_instance = await playwright_instance.chromium.launch(
            proxy=proxy,
            headless=headless,
            slow_mo=slow_mo,
            args=["--disable-http2"],
            **filtered_args,
        )
    elif browser == "firefox":
        filtered_args = __filter_kwargs(playwright_instance.firefox.launch, kwargs)
        browser_instance = await playwright_instance.firefox.launch(
            proxy=proxy,
            headless=headless,
            slow_mo=slow_mo,
            firefox_user_prefs={
                "http.spdy.enabled.http2": False,
                "network.http.http2.enabled": False,
                "network.http.http2.enabled.deps": False,
                "network.http.http2.websockets": False,
            },
            **filtered_args,
        )
    elif browser == "webkit":
        filtered_args = __filter_kwargs(playwright_instance.webkit.launch, kwargs)
        browser_instance = await playwright_instance.webkit.launch(
            proxy=proxy, headless=headless, slow_mo=slow_mo, **filtered_args
        )
    else:
        raise ValueError(
            "Invalid browser provided. Must be one of chromium, firefox or webkit."
        )

    device = playwright_instance.devices["iPhone 14 Pro Max"]
    device.pop("is_mobile")
    context = await browser_instance.new_context(**device)
    await context.clear_cookies()
    return context


async def download_video(
    initial_response: requests.Response,
    video_info: TikTokVideo,
    download_path: Union[str, None],
):
    """Uses the the browser request for the video to download the video. Valid for any download setting but less reliable.

    Args:
        initial_response (requests.Response): Response data from the /api/items/details request.
        video_info (TikTokVideo): The video data of the TikTok video.
        download_path (str | None): The path to download the video to. If None, uses current directory.
    """
    download_path = __validate_download_path(download_path)
    parsed_donwload_url = urlparse(video_info.download_url)
    download_url_host = parsed_donwload_url.hostname
    initial_request_headers = initial_response.request.headers
    video_request_headers = {
        "accept": "video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5",
        "accept-encoding": "identity",
        "accept-language": initial_request_headers["accept-language"],
        "connection": initial_request_headers["connection"],
        "cookie": initial_request_headers["cookie"],
        "host": download_url_host,
        "range": "bytes=0-",
        "referrer": "https://www.tiktok.com/",
        "user-agent": initial_request_headers["user-agent"],
        "accept-language": initial_request_headers["accept-language"],
    }

    save_path = f"{download_path}{video_info.post_id}.mp4"
    with requests.get(
        video_info.download_url, headers=video_request_headers, stream=True
    ) as r:
        r.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    video_info.file_path = save_path


async def download_slideshow(video_info: TikTokSlide, download_path: Union[str, None]):
    """For a given Slideshow post, download the images associated with it.

    Args:
        video_info (TikTokSlide): The Slideshow post data.
        download_path (str | None): The path to download the images to. If None, uses current directory.
    """
    download_path = __validate_download_path(download_path)

    images = []
    for idx, image_info in enumerate(video_info.images):
        image_url = image_info.get("image_url")[-1]
        file = f"{download_path}{idx+1}.jpeg"
        urlretrieve(image_url, file)
        images.append(file)

    video_info.images = images


async def __get_post(
    url: str,
    download: bool = True,
    browser: Literal["chromium", "firefox", "webkit"] = "firefox",
    proxy: Union[dict, None] = None,
    request_timeout: float = 5000,
    download_path: Union[str, None] = None,
    headless: Union[bool, None] = None,
    slow_mo: Union[float, None] = None,
    **kwargs,
) -> Union[TikTokSlide, TikTokVideo]:
    async with async_playwright() as playwright:

        context = await __get_browser(
            playwright, browser, proxy, headless, slow_mo, **kwargs
        )

        page = await context.new_page()
        # TODO: Reimplement CAPTACHA verification
        # await page.goto(url)
        # if not await verify_session(page):
        #     raise CaptchaFailedException(url=url)

        async with page.expect_request(
            lambda x: "/api/reflow/item/detail/" in x.url, timeout=request_timeout
        ) as request:
            await page.goto(url)

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
                    await download_slideshow(parsed_response, download_path)
                else:
                    await download_video(response, parsed_response, download_path)
            except:
                raise DownloadFailedException(url=url)

        return parsed_response


async def get_post(
    url: str,
    download: bool = True,
    browser: Literal["chromium", "firefox", "webkit"] = "firefox",
    proxy: Union[dict, None] = None,
    retries: int = 3,
    retry_delay: float = 500,
    request_timeout: float = 5000,
    download_path: Union[str, None] = None,
    headless: Union[bool, None] = None,
    slow_mo: Union[float, None] = None,
    **kwargs,
) -> Union[TikTokSlide, TikTokVideo]:
    """Get the information about a given video URL. If the `download` param is set to True, also download the video as an mp4 file or slideshow images as JPEG files.

    Args:
        url (str): The URL to get the information of.
        download (bool, optional): If the video should be downloaded locally. Defaults to True.
        browser (Literal[&quot;chromium&quot;, &quot;firefox&quot;, &quot;webkit&quot;], optional): The browser framework to use. If download is set to True, should be set to "firefox" as other browsers do not support downloads. Defaults to "firefox".
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

    if download and browser != "firefox":
        print("WARNING: Downloading is not supported on browsers other than firefox!")

    for x in range(retries + 1):
        try:
            result = await __get_post(
                url=url,
                download=download,
                browser=browser,
                proxy=proxy,
                request_timeout=request_timeout,
                download_path=download_path,
                headless=headless,
                slow_mo=slow_mo,
                **kwargs,
            )
            return result
        except Exception as e:
            if x < retries:
                await async_sleep(retry_delay / 1000.0)
                continue

            raise RetryLimitReached(e, retries, url)
