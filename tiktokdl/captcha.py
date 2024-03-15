import random
import time
from urllib.parse import parse_qs, urlparse

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page, Request
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from tiktokdl.image_processing import find_position, image_from_url

from typing import Tuple, Union


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


def __generate_random_captcha_steps(piece_position: Tuple[int, int],
                                    tip_y_value: int):
    x_position = piece_position[0]

    steps = []
    current_distance = 0
    relative_time = random.randint(100, 300)
    while current_distance < x_position:
        current_distance += random.randint(1, 4)
        relative_time += random.randint(6, 9)
        steps.append({
            "relative_time": relative_time,
            "x": current_distance,
            "y": tip_y_value
        })

    if steps[-1].get("x") < x_position or steps[-1].get("x") > x_position:
        steps.append({
            "relative_time": relative_time + random.randint(6, 9),
            "x": x_position,
            "y": tip_y_value
        })

    return steps


def __calculate_captcha_solution(captcha_get_data: dict) -> dict:
    data = captcha_get_data.get("data").get("challenges")[0].get("question")

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
        "reply": __generate_random_captcha_steps(position, tip_value)
    }

    return body


async def handle_captcha(playwright_page: Page,
                         attempts: int = 3,
                         timeout: Union[float, None] = 5000) -> bool:
    captcha_success_status = False
    attempt_count = 0

    while not captcha_success_status and attempt_count < attempts:
        try:
            async with playwright_page.expect_request(
                    lambda x: "/captcha/get?" in x.url,
                    timeout=timeout) as request:
                await playwright_page.wait_for_load_state("networkidle")
                request_value = await request.value
                response = await request_value.response()
                response_data = await response.json()

                captcha_solution = __calculate_captcha_solution(response_data)
                post_url_query_params = __get_captcha_response_params(
                    request_value.url)
                post_headers = await __get_captcha_response_headers(
                    request_value)
                base_url = urlparse(request_value.url).netloc
                api_request_context = playwright_page.request

                await playwright_page.wait_for_timeout(1000)
                captcha_status = await api_request_context.post(
                    f"https://{base_url}/captcha/verify",
                    data=captcha_solution,
                    headers=post_headers,
                    params=post_url_query_params)

                if captcha_status.status != 200:
                    return False

                captcha_status_data = await captcha_status.json()
                captcha_success_status = captcha_status_data.get(
                    "message") == "Verification complete"
                attempt_count += 1
                await playwright_page.locator("#verify-bar-close").click()

        except PlaywrightTimeoutError:
            return True
        except PlaywrightError:
            return False

    return captcha_success_status
