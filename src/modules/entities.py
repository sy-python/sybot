import dataclasses
import datetime


@dataclasses.dataclass(slots=True)
class User:
    id: int
    name: str
    platform: str


@dataclasses.dataclass(slots=True)
class Message:
    sender: User
    content: str
    timestamp: datetime.datetime
