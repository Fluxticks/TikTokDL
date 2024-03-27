import unittest
from datetime import datetime, timezone

from tiktokdl.post_data import TikTokSlide, TikTokVideo
import asyncio
from tiktokdl.download_post import get_post


class Test_TestTikTokURL(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_1 = "https://vm.tiktok.com/ZGeUuafAg/"
        self.url_2 = "https://vm.tiktok.com/ZGeAjeqVQ/"
        self.url_3 = "https://vm.tiktok.com/ZGefwPvNt/"  # slideshow

    def assert_data(self, expected_data, actual_data):
        self.assertIsNotNone(actual_data)

        self.assertEqual(expected_data.post_id, actual_data.post_id)
        self.assertEqual(expected_data.timestamp, actual_data.timestamp)

    def test_url_1(self):
        expected_data = TikTokVideo(
            url="https://tiktok.com/@ourgloriousgermany/video/7341431726746438944",
            post_id="7341431726746438944",
            author_username="ourgloriousgermany",
            author_display_name="OurGloriousGermany",
            author_avatar="some-url",
            author_url="https://tiktok.com/@ourgloriousgermany",
            post_download_setting=0,
            post_description="Watch till the end Frankfurt is unreal😍🇩🇪 Please "
            "comment which places you want next! #travel "
            "#frankfurt #world ",
            timestamp=datetime.fromtimestamp(1709310280, tz=timezone.utc),
            like_count=281600,
            share_count=8943,
            comment_count=5857,
            view_count=2400000,
            video_thumbnail="some-url",
        )

        actual_data = asyncio.run(get_post(url=self.url_1, download=False))

        self.assert_data(expected_data, actual_data)

    def test_url_2(self):
        expected_data = TikTokVideo(
            url="https://tiktok.com/@bbnotiktok/video/7337426987662822661",
            post_id="7337426987662822661",
            author_username="bbnotiktok",
            author_display_name="bbno$",
            author_avatar="some-url",
            author_url="https://tiktok.com/@bbnotiktok",
            post_download_setting=0,
            post_description="i love asmongold",
            timestamp=datetime.fromtimestamp(1708377853, tz=timezone.utc),
            like_count=70100,
            share_count=318,
            comment_count=194,
            view_count=794800,
            video_thumbnail="some-url",
            file_path=None,
        )

        actual_data = asyncio.run(get_post(url=self.url_2, download=False))

        self.assert_data(expected_data, actual_data)

    def test_url_3(self):
        expected_data = TikTokSlide(
            url="https://tiktok.com/@stimuli_adhd/video/7306931770056772896",
            post_id="7306931770056772896",
            author_username="stimuli_adhd",
            author_display_name="Stimuli ADHD",
            author_avatar="some-url",
            author_url="https://tiktok.com/@stimuli_adhd",
            post_download_setting=0,
            post_description="milly the intern is self aware to the point of "
            "upsetting herself x (tag yourself im the "
            "dismissive doctor)  #adhd #wrapped "
            "#spotifywrapped #memetherapy #swiftie "
            "#newlydiagnosedadhd @Spotify @spotifyuk ",
            timestamp=datetime.fromtimestamp(1701277633, tz=timezone.utc),
            like_count=60600,
            share_count=3381,
            comment_count=305,
            view_count=505500,
            images=[],
        )

        actual_data = asyncio.run(get_post(url=self.url_3, download=False))

        self.assert_data(expected_data, actual_data)
