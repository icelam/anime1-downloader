"""Custom exception types"""

class Error(Exception):
    """Base class for other exceptions"""
    pass

class EmptySearchResultError(Error):
    """Raised when search result is empty in search_animes_on_anime1()"""
    pass

class NoVideoFoundError(Error):
    """Raised when search result is empty in download_video()"""
    pass

class VideoStreamConnectionError(Error):
    """Raised when video stream connection isn't returning status code 200 in download_video()"""
    pass
