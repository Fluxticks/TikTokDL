class TikTokBaseException(Exception):

    def __init__(self, url: str, *args: object) -> None:
        super().__init__(*args)
        self.url = url


class CaptchaFailedException(TikTokBaseException):

    def __init__(self, url: str, *args: any):
        super().__init__(url, *args)


class DownloadFailedException(TikTokBaseException):

    def __init__(self, url: str, *args: any):
        super().__init__(url, *args)


class ResponseParseException(TikTokBaseException):

    def __init__(self, url: str, *args: any):
        super().__init__(url, *args)
