from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from tiktokdl.image_processing import find_position, image_from_url
from tiktokdl.video_data import TikTokVideo
from typing import Literal

__all__ = ["download"]


def __parse_video_info(page_source: str) -> TikTokVideo:
    pass


def __generate_random_captcha_steps(piece_position: tuple[int, int], tip_y_value: int):
    pass


def __calculate_captcha_solution(captcha_get_data: dict) -> dict:
    pass


async def __handle_captcha(playwright_page: Page) -> bool:
    pass


async def get_video(
    url: str,
    download: bool = True,
    browser: Literal["firefox",
                     "chromium",
                     "chrome",
                     "safari",
                     "webkit"] = "firefox"
) -> TikTokVideo:
    pass