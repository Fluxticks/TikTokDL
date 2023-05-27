# TikTokDL

A python package that downloads TikTok videos by URL

## Usage

1. Import the package

```python
from tiktokdl.download_video import get_video
```

2. Run the function in an async context

```python
video_url = ""

video_info = asyncio.run(
    get_video(
        video_url
    )
)
```
