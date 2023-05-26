class CaptchaFailedException(Exception):

    def __init__(self, url: str, *args: any):
        super().__init__(*args)
        self.url = url


class DownloadFailedException(Exception):

    def __init__(self, url: str, *args: any):
        super().__init__(*args)
        self.url = url