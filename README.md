# TikTokDL

A python package that downloads TikTok videos by URL

## TODO

- Enable downloading of video slideshows

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
from tiktokdl.download_video import get_video
```

3. Run the function in an async context

```python
video_url = ""

video_info = asyncio.run(
    get_video(
        video_url
    )
)
```
