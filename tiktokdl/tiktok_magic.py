"""A python module to store 'magic' values used to communicate with TikTok
"""

# CAPTCHA image width
MODIFIED_IMAGE_WIDTH = 340

# The subdomain used for CAPTCHA verification
CAPTCHA_HOST = "verification-i18n.tiktok.com"

# Headers to request a CAPTCHA
CAPTCHA_GET_HEADERS = {
    "Host": CAPTCHA_HOST,
    "Accept": " application/json, text/plain, */*",
    "Accept-Language": " en-US,en;q=0.5",
    "Accept-Encoding": " gzip, deflate, br",
    "Referer": " https://www.tiktok.com/",
    "Origin": " https://www.tiktok.com",
    "Sec-GPC": " 1",
    "Connection": " keep-alive",
    "Sec-Fetch-Dest": " empty",
    "Sec-Fetch-Mode": " cors",
    "Sec-Fetch-Site": " same-site",
}

# Headers to post a CAPTCHA solution
CAPTCHA_POST_HEADERS = {
    **CAPTCHA_GET_HEADERS,
    "Content-Type": " application/json;charset=utf-8",
}

# Magic numbers used for CAPTCHA verification
OS_TYPE = 2
CHALLENGE_CODE = 99999
CAPTCHA_VERSION = 2

# The cookie that stores the device_id of the current session.
DEVICE_ID_TARGET_COOKIE = "__tea_cache_tokens"
