import unittest
from datetime import datetime

from tiktokdl.post_data import TikTokSlide, TikTokVideo
import asyncio
from tiktokdl.download_post import get_post


class Test_TestTikTokURL(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_1 = "https://vm.tiktok.com/ZGeUuafAg/"
        self.url_2 = "https://vm.tiktok.com/ZGeUuafAg/"
        self.url_3 = "https://vm.tiktok.com/ZGefwPvNt/"  # slideshow

    def assert_data(self, expected_data, actual_data):
        self.assertIsNotNone(actual_data)

        self.assertEqual(expected_data.post_id, actual_data.post_id)
        self.assertEqual(expected_data.author_username,
                         actual_data.author_username)

    def test_url_1(self):
        expected_data = TikTokVideo(
            url='https://tiktok.com/@ben_reilly_/video/7341431726746438944',
            post_id='7341431726746438944',
            author_username='ben_reilly_',
            author_display_name='OurGloriousGermany',
            author_avatar='some-url',
            author_url='https://tiktok.com/@ben_reilly_',
            post_download_setting=0,
            post_description='Watch till the end Frankfurt is unreal😍🇩🇪 Please '
            'comment which places you want next! #travel '
            '#frankfurt #world ',
            timestamp=datetime(2024, 3, 1, 17, 24, 40),
            like_count=281600,
            share_count=8943,
            comment_count=5857,
            view_count=2400000,
            video_thumbnail="some-url")

        actual_data = asyncio.run(get_post(url=self.url_1, download=False))

        self.assert_data(expected_data, actual_data)

    def test_url_2(self):
        expected_data = TikTokVideo(
            url='https://tiktok.com/@ben_reilly_/video/7341431726746438944',
            post_id='7341431726746438944',
            author_username='ben_reilly_',
            author_display_name='OurGloriousGermany',
            author_avatar='some-url',
            author_url='https://tiktok.com/@ben_reilly_',
            post_download_setting=0,
            post_description='Watch till the end Frankfurt is unreal😍🇩🇪 Please '
            'comment which places you want next! #travel '
            '#frankfurt #world ',
            timestamp=datetime(2024, 3, 1, 17, 24, 40),
            like_count=281600,
            share_count=8943,
            comment_count=5857,
            view_count=2400000,
            video_thumbnail="some-url")

        actual_data = asyncio.run(get_post(url=self.url_2, download=False))

        self.assert_data(expected_data, actual_data)

    def test_url_3(self):
        expected_data = TikTokSlide(
            url='https://tiktok.com/@stimuli_adhd/video/7306931770056772896',
            post_id='7306931770056772896',
            author_username='stimuli_adhd',
            author_display_name='Stimuli ADHD',
            author_avatar='some-url',
            author_url='https://tiktok.com/@stimuli_adhd',
            post_download_setting=0,
            post_description='milly the intern is self aware to the point of '
            'upsetting herself x (tag yourself im the '
            'dismissive doctor)  #adhd #wrapped '
            '#spotifywrapped #memetherapy #swiftie '
            '#newlydiagnosedadhd @Spotify @spotifyuk ',
            timestamp=datetime(2023, 11, 29, 18, 7, 13),
            like_count=60600,
            share_count=3381,
            comment_count=305,
            view_count=505500,
            images=[])

        actual_data = asyncio.run(get_post(url=self.url_3, download=False))

        self.assert_data(expected_data, actual_data)
