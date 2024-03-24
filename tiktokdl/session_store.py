import time
import json
from playwright.async_api import Page, Cookie
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from typing import List
from tiktokdl.tiktok_magic import DEVICE_ID_TARGET_COOKIE


async def wait_for_cookie(
    page: Page, target_cookie: str, timeout: float, timeout_interval: float = 100
) -> str:
    """Wait for a given cookie to be set and then get the value.

    Args:
        page (Page): The page to get the cookie from.
        target_cookie (str): The name of the cookie to wait for.
        timeout (float): The maximum time to wait in MS before timing out.
        timeout_interval (float, optional): How long to wait between checks for the cookie to be set in MS. Defaults to 100.

    Raises:
        PlaywrightTimeoutError: If the given timeout is exceeded, a playwright TimeoutError is raised.

    Returns:
        str: The value of the cookie set.
    """

    start_time = time.time()
    while True:
        cookies = await page.context.cookies()
        now = time.time()
        for item in cookies:
            if item.get("name") == target_cookie:
                return item.get("value")

        if now - start_time > timeout:
            raise PlaywrightTimeoutError(
                f"Timeout exceeded {timeout}ms while waiting for {target_cookie} to be set."
            )

        await page.wait_for_timeout(timeout_interval)


def get_ms_token(cookies: List[Cookie]) -> str:
    """Get the msToken of the current session.

    Args:
        cookies (List[Cookie]): The cookies of the current session.

    Returns:
        str | None: The msToken of the current session, or None if the cookie is not present.
    """
    target_cookie_name = "msToken"
    msToken = None
    for item in cookies:
        if item.get("name") == target_cookie_name and item.get("secure"):
            msToken = item.get("value")

    return msToken


async def get_device_id(
    page: Page, timeout: float, timeout_interval: float = 100
) -> int:
    """Get the device_id / did of the current session. As this cookie is not set upon accessing TikTok, it must be awaited until it is.

    Args:
        page (Page): The page to get the device id from.
        timeout (float): The maximum time to wait in MS for the cookie to be set.
        timeout_interval (float, optional): How long to wait between checks for the cookie to be set in MS. Defaults to 100.

    Raises:
        PlaywrightTimeoutError: If the given timeout is exceeded, a playwright TimeoutError is raised.

    Returns:
        int: The device id of the current session.
    """
    start_time = time.time()
    while True:
        storage = await page.context.storage_state()
        local_storage = storage.get("origins")[0].get("localStorage")
        now = time.time()
        for item in local_storage:
            if DEVICE_ID_TARGET_COOKIE in item.get("name"):
                data = json.loads(item.get("value"))
                try:
                    device_id = int(data.get("user_unique_id"))
                    return device_id
                except:
                    continue

        if now - start_time > timeout:
            raise PlaywrightTimeoutError(
                f"Timeout exceeded {timeout}ms while waiting for {DEVICE_ID_TARGET_COOKIE} to be set."
            )

        await page.wait_for_timeout(timeout_interval)


async def get_verify_fp(page: Page, timeout: float) -> str:
    """Get the VerifyFp value assigned to the current session.

    Args:
        page (Page): The page to get the VerifyFp of.
        timeout (float): The maximum time to wait in MS for the cookie to be set.

    Returns:
        str: The VerifyFp string of the current session.
    """
    return await wait_for_cookie(page, "s_v_web_id", timeout)
