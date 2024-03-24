import cv2 as cv
from random import randint

from playwright.async_api import Page

from tiktokdl.image_processing import find_position, image_from_url
from tiktokdl.tiktok_magic import (
    CAPTCHA_GET_HEADERS,
    CAPTCHA_HOST,
    CAPTCHA_POST_HEADERS,
    CAPTCHA_VERSION,
    CHALLENGE_CODE,
    MODIFIED_IMAGE_WIDTH,
    OS_TYPE,
)
from tiktokdl.session_store import get_device_id, get_ms_token, get_verify_fp

from typing import Dict, Tuple


def __generate_captcha_response(
    captcha_solution: Dict, captcha_id: str, verify_id: str
) -> Dict:
    data = {
        "modified_img_width": MODIFIED_IMAGE_WIDTH,
        "id": captcha_id,
        "mode": "slide",
        "reply": captcha_solution,
        "reply2": captcha_solution,
    }

    response = {**data, "verify_id": verify_id, "version": CAPTCHA_VERSION}
    return response


def __generate_random_captcha_steps(
    target_position, tip_y_value: int
) -> Tuple[Dict, Dict]:
    """Generate a random sequence of movements to simulate a human sliding the piece to the correct position.

    Args:
        target_position (int): The target piece X position.
        tip_y_value (int): The tip_y value given by the challenge.

    Returns:
        Tuple[Dict, Dict]: First dictionary stores the solution required by TikTok. Second dictionary stores the deltas between each step.
    """
    current_position = 0
    current_time = randint(200, 400)
    steps = []
    deltas = []
    while current_position < target_position:
        time_step = randint(8, 9)
        move_step = randint(1, 6)

        current_time += time_step
        current_position += move_step

        steps.append(
            {"x": current_position, "y": target_position, "relative_time": current_time}
        )

        deltas.append({"x": move_step, "y": randint(-2, 2), "time": time_step})

    if steps[-1]["x"] > target_position or steps[-1]["x"] < target_position:
        time_step = randint(8, 9)
        move_step = target_position - steps[-1]["x"]
        steps.append(
            {
                "x": target_position,
                "y": tip_y_value,
                "relatie_time": current_time + time_step,
            }
        )

        deltas.append({"x": move_step, "y": randint(-2, 2), "time": time_step})

    return steps, deltas


def __calculate_image_scale(
    original_width: int, output_width: int = MODIFIED_IMAGE_WIDTH
) -> float:
    """Get the scale to modify the image by to get the desired modified image width.

    Args:
        original_width (int): The original width of the image.
        output_width (int, optional): The output image width. Defaults to MODIFIED_IMAGE_WIDTH.

    Returns:
        float: The scale to modify the original width and height by to get the desired width.
    """
    return float(output_width) / float(original_width)


def __solve_captcha(challenge_data: Dict) -> Dict:
    background = image_from_url(challenge_data.get("url_1"))
    piece = image_from_url(challenge_data.get("url_2"))

    _, original_width, _ = background.shape
    ratio = __calculate_image_scale(original_width)

    background = cv.resize(background, (0, 0), fx=ratio, fy=ratio)
    piece = cv.resize(piece, (0, 0), fx=ratio, fy=ratio)

    x, y = find_position(background, piece)
    h, w, _ = piece.shape

    i = cv.rectangle(background, (x, y), (x + w, y + h), 255, 2)

    steps, _ = __generate_random_captcha_steps(x, challenge_data.get("tip_y"))
    return steps


def __parse_captcha_challenge(challenge_response: Dict) -> Dict:
    """Get the required information from the challenge given by TikTok.

    Args:
        challenge_response (Dict): The raw dictionary of the challenge given by TikTok.

    Returns:
        Dict: The challenge data.
    """
    data = challenge_response.get("data")
    captcha_id = data.get("id")
    verify_id = data.get("verify_id")
    mode = data.get("mode")

    question = data.get("question")
    url_1 = question.get("url1")
    url_2 = question.get("url2")
    tip_y = question.get("tip_y")

    return {
        "captcha_id": captcha_id,
        "verify_id": verify_id,
        "mode": mode,
        "url_1": url_1,
        "url_2": url_2,
        "tip_y": tip_y,
    }


async def __get_challenge(
    page: Page,
    verify_fp: str,
    device_id: int,
    ms_token: str,
    timeout_interval: float = 100,
    max_requests: int = 5,
) -> Dict:
    """Get a challenge from TikTok that can be used to verify the current session.

    Args:
        page (Page): The page to get the session of.
        verify_fp (str): The VerifyFp string of the current session.
        device_id (int): The Device ID of the current session.
        ms_token (str): The msToken of the current session.
        timeout_interval (float, optional): How long to wait between requesting a new challenge when the given challenge is not 'slide'. Defaults to 100.
        max_requests (int, optional): The maximum number of requests to make. Defaults to 5.

    Returns:
        Dict: The required challenge data that can be used to verify the challenge.
    """
    api_request_context = page.request
    challenge_type = None
    request_count = 0

    while challenge_type != "slide" and request_count < max_requests:
        await page.wait_for_timeout(timeout_interval)
        captcha_request = await api_request_context.fetch(
            f"https://{CAPTCHA_HOST}/captcha/get",
            params={
                "did": device_id,
                "device_id": device_id,
                "os_type": OS_TYPE,
                "fp": verify_fp,
                "type": "verify",
                "subtype": "slide",
                "msToken": ms_token,
            },
            method="GET",
            headers=CAPTCHA_GET_HEADERS,
        )

        data = await captcha_request.json()
        challenge_type = data.get("data").get("mode")
        request_count += 1

    return __parse_captcha_challenge(data)


async def verify_session(page: Page, cookie_timeout: float = 30000) -> bool:
    """Complete a CAPTCHA to verify the current session for TikTok.

    Args:
        page (Page): The page to verify the session of.
        cookie_timeout (float, optional): How long to wait for cookies to appear. Defaults to 30000.

    Returns:
        bool: If the session verification was successful.
    """
    cookies = await page.context.cookies()
    verify_fp = await get_verify_fp(page, cookie_timeout)
    device_id = await get_device_id(page, cookie_timeout)
    ms_token = get_ms_token(cookies)

    captcha_challenge = await __get_challenge(page, verify_fp, device_id, ms_token)

    captcha_solution = __solve_captcha(captcha_challenge)

    challenge_response_data = __generate_captcha_response(
        captcha_solution, captcha_challenge.get("captcha_id"), verify_fp
    )

    captcha_response_request = await page.request.fetch(
        f"https://{CAPTCHA_HOST}/captcha/verify",
        headers=CAPTCHA_POST_HEADERS,
        data=challenge_response_data,
        params={
            "did": device_id,
            "device_id": device_id,
            "os_type": OS_TYPE,
            "fp": verify_fp,
            "type": "verify",
            "subtype": "slide",
            "mode": "slide",
            "msToken": ms_token,
            "challenge_code": CHALLENGE_CODE,
        },
        method="POST",
    )

    captcha_response = await captcha_response_request.json()
    return captcha_response.get("message") == "Verification complete"
