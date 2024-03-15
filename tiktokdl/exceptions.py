class TikTokBaseException(Exception):

    def __init__(self, url: str, *args: object) -> None:
        super().__init__(*args)
        self.url = url

    def __str__(self):
        return f"TikTok exception occured when accessing {self.url}"


class CaptchaFailedException(TikTokBaseException):

    def __init__(self, url: str, *args: any):
        super().__init__(url, *args)


class DownloadFailedException(TikTokBaseException):

    def __init__(self, url: str, *args: any):
        super().__init__(url, *args)


class ResponseParseException(TikTokBaseException):

    def __init__(self, url: str, *args: any):
        super().__init__(url, *args)


class RetryLimitReached(Exception):

    def __init__(self, error: Exception, retries: int, url: str, *args: any):
        super().__init__(*args)
        self.offending_error = error
        self.max_retries = retries
        self.url = url

    def __str__(self):
        return f"The maximum number of retries was reached ({self.max_retries}). The last error that occured was:\n\n {self.offending_error.__class__.__name__}: {self.offending_error!s}"
