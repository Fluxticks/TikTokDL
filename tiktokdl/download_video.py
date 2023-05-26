from random import random
from typing import Literal

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from tiktokdl.exceptions import CaptchaFailedException, DownloadFailedException
from tiktokdl.image_processing import find_position, image_from_url
from tiktokdl.video_data import TikTokVideo

__all__ = ["download"]


def __parse_video_info(page_source: str) -> TikTokVideo:
    pass


def __generate_random_captcha_steps(piece_position: tuple[int, int], tip_y_value: int):
    pass


def __calculate_captcha_solution(captcha_get_data: dict) -> dict:
    pass


async def __handle_captcha(playwright_page: Page) -> bool:
    pass


async def __random_timeout_duration(playwright_page: Page, min_timeout: int, max_timout: int):
    pass


async def __close_popups(playwright_page: Page) -> int:
    pass


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