import unittest
from datetime import datetime

from tiktokdl.post_data import TikTokSlide, TikTokVideo
import asyncio
from tiktokdl.download_post import get_post


class Test_TestTikTokURL(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_1 = "https://vm.tiktok.com/ZGeYy3Ekf/"
        self.url_2 = "https://vm.tiktok.com/ZGeY1YeXk/"
        self.url_3 = "https://vm.tiktok.com/ZGeYA9CJ4/"  # slideshow

    def assert_data(self, expected_data, actual_data):
        self.assertIsNotNone(actual_data)

        self.assertEqual(expected_data.post_id, actual_data.post_id)
        self.assertEqual(expected_data.author_username,
                         actual_data.author_username)

    def test_url_1(self):
        expected_data = TikTokVideo(
            url="https://tiktok.com/@jimdoga/video/7302355630109773057",
            post_id="7302355630109773057",
            author_username="jimdoga",
            author_display_name="Jimdoga",
            author_avatar="some-url",
            author_url="https://tiktok.com/@jimdoga",
            post_download_setting=0,
            post_description="never joining an smp late again... #minecraft "
            "#minecraftmoment #fyp #mcyt #herobrine #foryou "
            "#foryoupage",
            timestamp=datetime(2023, 11, 17, 10, 9, 26),
            like_count=205900,
            share_count=1572,
            comment_count=778,
            view_count=1900000,
            video_thumbnail="some-url",
            file_path=None)

        actual_data = asyncio.run(get_post(url=self.url_1, download=False))

        self.assert_data(expected_data, actual_data)

    def test_url_2(self):
        expected_data = TikTokVideo(
            url="https://tiktok.com/@dafuqboom_94/video/7307437770128067871",
            post_id="7307437770128067871",
            author_username="dafuqboom_94",
            author_display_name="Dafuq!?Boom!",
            author_avatar="some-url",
            author_url="https://tiktok.com/@dafuqboom_94",
            post_download_setting=0,
            post_description="The End 🤣🤣 #funny #funnyvideos #animals #dog "
            "#cat #pet #viarl #foryou #fyp (540)",
            timestamp=datetime(2023, 12, 1, 2, 50, 51),
            like_count=211500,
            share_count=8454,
            comment_count=2016,
            view_count=3500000,
            video_thumbnail="some-url",
            file_path=None)

        actual_data = asyncio.run(get_post(url=self.url_2, download=False))

        self.assert_data(expected_data, actual_data)

    def test_url_3(self):
        expected_data = TikTokSlide(
            url=
            "https://tiktok.com/@the.finals.content/video/7316903402024324384",
            post_id="7316903402024324384",
            author_username="the.finals.content",
            author_display_name="TheFinals Content",
            author_avatar="some-url",
            author_url="https://tiktok.com/@the.finals.content",
            post_download_setting=0,
            post_description="... #thefinals #thefinalsgame "
            "#thefinalsgameplay ",
            timestamp=datetime(2023, 12, 26, 15, 2, 17),
            like_count=411500,
            share_count=15000,
            comment_count=6382,
            view_count=4400000,
            images=[])

        actual_data = asyncio.run(get_post(url=self.url_3, download=False))

        self.assert_data(expected_data, actual_data)
