![Main Workflow](https://github.com/Fluxticks/TikTokDL/actions/workflows/main.yml/badge.svg) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tiktok-dlpy)

# TikTokDL

A python package to download TikTok videos or slideshows by URL without needing to login.

## TODO

- Allow usage of other browsers (eg. Chromium)
  - Requires a fix regarding response body protocol error (similar to [this](https://github.com/microsoft/playwright/issues/26388) issue)

## Usage

1. Install the package

```bash
$ pip install tiktok-dlpy
```

2. Ensure that playwright has been installed

```bash
$ python -m playwright install
$ python -m playwright install-deps
```

2. Import the package

```python
from tiktokdl.download_post import get_post
```

3. Run the function in an async context

```python
video_or_slide_url = ""

post_info = asyncio.run(
    get_post(
        video_or_slide_url
    )
)
```
