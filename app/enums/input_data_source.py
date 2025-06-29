from enum import Enum


class InputDataSource(Enum):
    USER_TYPED = "user_typed"
    MEET_TRANSCRIPT = "meet_transcript"
    SLACK = "slack"
    YT_TRANSCRIPT = "yt_transcript"
    WEB_PAGE = "web_page"
    PDF = "pdf"
    CHAT = "chat"
