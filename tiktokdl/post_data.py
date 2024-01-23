from dataclasses import dataclass
from datetime import datetime

from typing import List


@dataclass()
class TikTokPost:
    url: str
    post_id: str
    author_username: str
    author_display_name: str
    author_avatar: str
    author_url: str
    post_download_setting: int
    post_description: str
    timestamp: datetime
    like_count: int
    share_count: int
    comment_count: int
    view_count: int


@dataclass()
class TikTokVideo(TikTokPost):
    video_thumbnail: str
    file_path: str = None


@dataclass()
class TikTokSlide(TikTokPost):
    images: List[str] = None
