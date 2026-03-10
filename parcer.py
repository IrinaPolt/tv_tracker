from datetime import datetime
import json

from psycopg_pool import ConnectionPool
from selenium import webdriver

from models import ScheduleLine
from repositories import ChannelRepository, SubscriptionRepository
import config


def create_safari_driver() -> webdriver.Safari:
    options = webdriver.SafariOptions()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    return webdriver.Safari(options=options)


def create_connection_pool() -> ConnectionPool:
    pool = ConnectionPool(
        max_size=config.DB_MAX_CONNECTIONS,
        conninfo=config.DB_URL,
    )
    pool.open()
    return pool


def load_channels() -> list[dict]:
    with open("channels.json", "r") as file:
        return json.load(file)


def get_channel_state(driver: webdriver.Safari, link: str) -> dict:
    driver.get(link)
    return driver.execute_script("return window.__INITIAL_STATE__")


def get_or_create_channel(channel_repo: ChannelRepository, name: str):
    status, channel = channel_repo.check_channel(name)

    if not status:
        print(channel)
        return None

    if not channel:
        status, channel = channel_repo.add_channel(name)
        if not status:
            print(channel)
            return None

    return channel


def process_schedule(state: dict, channel_id: int, channel_repo, subscription_repo):
    events = state["channel"]["schedule"]["events"]

    for event in events:
        title = event["title"]

        status, subscriptions = subscription_repo.get_all(title=title)
        if not status or not subscriptions:
            continue

        start = datetime.fromisoformat(event["start"]).replace(tzinfo=None)
        end = datetime.fromisoformat(event["finish"]).replace(tzinfo=None)

        for subscription in subscriptions:
            schedule_line = ScheduleLine(
                id=None,
                channel_id=channel_id,
                subscription_id=subscription.id,
                utc_time_start=start,
                utc_time_end=end,
            )

            status, result = channel_repo.add_to_schedule(schedule_line)

            if not status:
                print(result)


def main():
    driver = create_safari_driver()
    pool = create_connection_pool()
    channels = load_channels()

    try:
        for channel in channels:
            link = channel["link"]
            name = channel["name"]

            state = get_channel_state(driver, link)

            with pool.connection() as connection:
                channel_repo = ChannelRepository(connection)
                subscription_repo = SubscriptionRepository(connection)

                channel_data = get_or_create_channel(channel_repo, name)
                if not channel_data:
                    continue

                process_schedule(
                    state,
                    channel_data.id,
                    channel_repo,
                    subscription_repo,
                )

    finally:
        driver.quit()
        pool.close()


if __name__ == "__main__":
    main()
