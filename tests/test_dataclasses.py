import unittest
from tiktokdl.post_data import TikTokPost, TikTokVideo, TikTokSlide
from datetime import datetime

POST = TikTokPost(
    url="https://tiktok.com",
    post_id="1234",
    author_username="username",
    author_display_name="displayname",
    author_avatar="avatar",
    author_url="https://tiktok.com",
    post_download_setting=1,
    post_description="description",
    timestamp=datetime(1997, 1, 1),
    like_count=1,
    share_count=2,
    comment_count=3,
    view_count=4,
)


class Test_TestTikTokPost(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post = POST

    def test_url(self):
        self.assertEqual(self.post.url, "https://tiktok.com")

    def test_post_id(self):
        self.assertEqual(self.post.post_id, "1234")

    def test_author_username(self):
        self.assertEqual(self.post.author_username, "username")

    def test_author_display_name(self):
        self.assertEqual(self.post.author_display_name, "displayname")

    def test_author_avatar(self):
        self.assertEqual(self.post.author_avatar, "avatar")

    def test_author_url(self):
        self.assertEqual(self.post.author_url, "https://tiktok.com")

    def test_post_download_setting(self):
        self.assertEqual(self.post.post_download_setting, 1),

    def test_timestamp(self):
        self.assertEqual(self.post.timestamp, datetime(1997, 1, 1))

    def test_like_count(self):
        self.assertEqual(self.post.like_count, 1)

    def test_share_count(self):
        self.assertEqual(self.post.share_count, 2)

    def test_comment_count(self):
        self.assertEqual(self.post.comment_count, 3)

    def test_view_count(self):
        self.assertEqual(self.post.view_count, 4)


class Test_TestTikTokVideo(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post = POST
        self.video_post = TikTokVideo(**self.post.__dict__, video_thumbnail="thumbnail")

    def test_convert_from_super(self):
        self.assertEqual(self.post.url, self.video_post.url)
        self.assertEqual(self.post.post_id, self.video_post.post_id)
        self.assertEqual(self.post.author_username, self.video_post.author_username)
        self.assertEqual(
            self.post.author_display_name, self.video_post.author_display_name
        )
        self.assertEqual(self.post.author_avatar, self.video_post.author_avatar)
        self.assertEqual(self.post.author_url, self.video_post.author_url)
        self.assertEqual(
            self.post.post_download_setting, self.video_post.post_download_setting
        )
        self.assertEqual(self.post.post_description, self.video_post.post_description)
        self.assertEqual(self.post.timestamp, self.video_post.timestamp)
        self.assertEqual(self.post.like_count, self.video_post.like_count)
        self.assertEqual(self.post.share_count, self.video_post.share_count)
        self.assertEqual(self.post.comment_count, self.video_post.comment_count)
        self.assertEqual(self.post.view_count, self.video_post.view_count)

    def test_video_thumbnail(self):
        self.assertEqual(self.video_post.video_thumbnail, "thumbnail")

    def test_file_path(self):
        self.assertIsNone(self.video_post.file_path)


class Test_TestTikTokSlide(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post = POST
        self.slide_post = TikTokSlide(**self.post.__dict__)

    def test_convert_from_super(self):
        self.assertEqual(self.post.url, self.slide_post.url)
        self.assertEqual(self.post.post_id, self.slide_post.post_id)
        self.assertEqual(self.post.author_username, self.slide_post.author_username)
        self.assertEqual(
            self.post.author_display_name, self.slide_post.author_display_name
        )
        self.assertEqual(self.post.author_avatar, self.slide_post.author_avatar)
        self.assertEqual(self.post.author_url, self.slide_post.author_url)
        self.assertEqual(
            self.post.post_download_setting, self.slide_post.post_download_setting
        )
        self.assertEqual(self.post.post_description, self.slide_post.post_description)
        self.assertEqual(self.post.timestamp, self.slide_post.timestamp)
        self.assertEqual(self.post.like_count, self.slide_post.like_count)
        self.assertEqual(self.post.share_count, self.slide_post.share_count)
        self.assertEqual(self.post.comment_count, self.slide_post.comment_count)
        self.assertEqual(self.post.view_count, self.slide_post.view_count)

    def test_images(self):
        self.assertIsNone(self.slide_post.images)
