from dataclasses import dataclass


@dataclass
class User:
    id: int | None
    telegram_id: int
    timezone: str | None


@dataclass
class Subscription:
    id: int | None
    user_id: int
    title: str
