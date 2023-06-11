from dataclasses import dataclass
from datetime import datetime


@dataclass()
class TikTokVideo:
    url: str
    video_id: str
    author_username: str
    author_display_name: str
    author_avatar: str
    author_url: str
    video_download_setting: int
    video_description: str
    timestamp: datetime
    like_count: int
    share_count: int
    comment_count: int
    view_count: int
    video_thumbnail: str
    file_path: str = None