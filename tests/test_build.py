from unittest import IsolatedAsyncioTestCase
from tiktokdl.download_post import get_post
from tiktokdl.post_data import TikTokPost, TikTokSlide, TikTokVideo
import datetime


class Test_TestTikTokBuild(IsolatedAsyncioTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.url_1 = "https://www.tiktok.com/t/ZGe3v8d7T/"  # Video
        self.url_2 = "https://www.tiktok.com/t/ZGe3vMumb/"  # Video
        self.url_3 = "https://www.tiktok.com/t/ZGe37v7N4/"  # Slideshow
        self.url_4 = "https://www.tiktok.com/t/ZGe3vMsCN/"  # Slideshow

    def assert_expected_values(self, expected: TikTokPost, actual: TikTokPost):
        self.assertIsNotNone(actual)

        self.assertEqual(expected.post_id, actual.post_id)
        self.assertEqual(expected.author_id, actual.author_id)
        self.assertEqual(expected.url, actual.url)

    async def test_url_1(self):
        expected = TikTokVideo(
            url="https://tiktok.com/@121078843527806976/video/7406020582829051179",
            post_id="7406020582829051179",
            author_username="sabrinacarpenter",
            author_display_name="Sabrina Carpenter",
            author_avatar="",
            author_url="https://tiktok.com/@sabrinacarpenter",
            author_id="121078843527806976",
            post_description="How to host your own short n' sweet listening "
            "party. Midnight tonight 💋 @Spotify ",
            timestamp=datetime.datetime(
                2024, 8, 22, 17, 42, 30, tzinfo=datetime.timezone.utc
            ),
            like_count=0,
            share_count=0,
            comment_count=0,
            view_count=0,
            post_download_setting=-1,
            video_thumbnail="",
            download_url="",
            file_path="",
        )

        actual = await get_post(url=self.url_1)

        self.assert_expected_values(expected, actual)

    async def test_url_2(self):
        expected = TikTokVideo(
            url="https://tiktok.com/@6742943291057521669/video/7364553193529052462",
            post_id="7364553193529052462",
            author_username="chappellroan",
            author_display_name="chappell roan",
            author_avatar="",
            author_url="https://tiktok.com/@chappellroan",
            author_id="6742943291057521669",
            post_description="ur dream girl's dream girl",
            timestamp=datetime.datetime(
                2024, 5, 2, 23, 47, 53, tzinfo=datetime.timezone.utc
            ),
            like_count=0,
            share_count=0,
            comment_count=0,
            view_count=0,
            post_download_setting=-1,
            video_thumbnail="",
            download_url="",
            file_path="",
        )

        actual = await get_post(url=self.url_2)

        self.assert_expected_values(expected, actual)

    async def test_url_3(self):
        expected = TikTokSlide(
            url="https://tiktok.com/@7015519970671821830/video/7306931770056772896",
            post_id="7306931770056772896",
            author_username="stimuli_adhd",
            author_display_name="Stimuli ADHD",
            author_avatar="",
            author_url="https://tiktok.com/@stimuli_adhd",
            author_id="7015519970671821830",
            post_description="milly the intern is self aware to the point of "
            "upsetting herself x (tag yourself im the "
            "dismissive doctor)  #adhd #wrapped "
            "#spotifywrapped #memetherapy #swiftie "
            "#newlydiagnosedadhd @Spotify @spotifyuk ",
            timestamp=datetime.datetime(
                2023, 11, 29, 17, 7, 13, tzinfo=datetime.timezone.utc
            ),
            like_count=0,
            share_count=0,
            comment_count=0,
            view_count=0,
            post_download_setting=-1,
            images=[],
        )

        actual = await get_post(url=self.url_3)

        self.assert_expected_values(expected, actual)

    async def test_url_4(self):
        expected = TikTokSlide(
            url="https://tiktok.com/@7248236920656036890/video/7281699514681920801",
            post_id="7281699514681920801",
            author_username="zooview2",
            author_display_name="ZooView",
            author_avatar="",
            author_url="https://tiktok.com/@zooview2",
            author_id="7248236920656036890",
            post_description="#slideshow #memes #capybara #cat #dog ",
            timestamp=datetime.datetime(
                2023, 9, 22, 17, 13, 9, tzinfo=datetime.timezone.utc
            ),
            like_count=0,
            share_count=0,
            comment_count=0,
            view_count=0,
            post_download_setting=-1,
            images=[],
        )

        actual = await get_post(url=self.url_4)

        self.assert_expected_values(expected, actual)
