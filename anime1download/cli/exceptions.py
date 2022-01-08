"""Custom exception types"""

# pylint: disable=unnecessary-pass, super-init-not-called

class Error(Exception):
    """Base class for other exceptions"""
    pass

class EmptySearchResultError(Error):
    """Raised when search result is empty in search_animes_on_anime1()"""
    def __init__(self, keyword):
        self.keyword = keyword

    def __str__(self):
        return f'輸入的關鍵字「{self.keyword}」找不到任何東西'

class NoVideoFoundError(Error):
    """Raised when failed to get player url in download_video()"""
    def __init__(self, video_info):
        self.video_info = video_info

    def __str__(self):
        return f'找不到影片地址: {self.video_info}'

class VideoStreamConnectionError(Error):
    """Raised when video stream connection isn't returning status code 200 in download_video()"""
    def __init__(self, video_info):
        self.video_info = video_info

    def __str__(self):
        return f'無法加載影片: {self.video_info}'
