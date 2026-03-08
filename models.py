from dataclasses import dataclass


@dataclass
class Channel:
    id: int | None
    name: str


@dataclass
class User:
    id: int | None
    telegram_id: int
    timezone: str | None


@dataclass
class ScheduleLine:
    id: int | None
    channel_id: int
    subscription_id: int
    utc_time_start: str
    utc_time_end: str


@dataclass
class Show:
    id: int
    channel_name: str
    show_title: str
    time_start: str
    time_end: str


@dataclass
class Subscription:
    id: int | None
    user_id: int
    title: str
