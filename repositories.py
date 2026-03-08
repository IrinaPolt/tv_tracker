from datetime import datetime
from typing import Union

from psycopg import Connection, Error

from models import Channel, User, ScheduleLine, Show, Subscription



class UserRepository:
    def __init__(self, connection: Connection):
        self.connection = connection


    async def get_by_telegram_id(self, telegram_id:int) -> tuple[bool, Union[User, str, None]]:
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT id, telegram_id, timezone
                    FROM users
                    WHERE telegram_id=%s
                """, (telegram_id, ))
                row = await cursor.fetchone()
        except Error as e:
            return False, str(e)

        if not row:
            return True, None

        return True, User(*row)


    async def add(self, telegram_id:int) -> tuple[bool, Union[User, str]]:
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO users (telegram_id)
                    VALUES (%s)
                    RETURNING id, telegram_id, timezone
                """, (telegram_id, ))
                row = await cursor.fetchone()
        except Error as e:
            return False, str(e)

        return True, User(*row)


    async def update(self, telegram_id: int, data: dict) -> tuple[bool, Union[User, str]]:
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    UPDATE users SET timezone = %s
                    WHERE telegram_id = %s
                    RETURNING id, telegram_id, timezone
                """, (data.get("timezone"), telegram_id))
                row = await cursor.fetchone()
        except Error as e:
            return False, str(e)

        return True, User(*row)


class ChannelRepository:
    def __init__(self, connection: Connection):
        self.connection = connection


    def add_channel(self, channel_name: str) -> tuple[bool, Union[str, dict]]:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO channels (name)
                    VALUES (%s)
                    RETURNING id, name
                """, (channel_name, ))
                channel = cursor.fetchone()
        except Error as e:
            return False, str(e)
    
        return True, Channel(*channel)


    def check_channel(self, channel_name: str) -> tuple[bool, Union[str, dict, None]]:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM channels WHERE name=%s
                """, (channel_name, ))
                channel = cursor.fetchone()
        except Error as e:
            return False, str(e)
    
        if not channel:
            return True, None
    
        return True, Channel(*channel)


    def remove_outdated_schedule(self) -> tuple[bool, str]:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM schedule
                    WHERE utc_time_end < NOW() AT TIME ZONE 'UTC'
                """)
        except Error as e:
            return False, str(e)
        
        return True, ""


    def add_to_schedule(self, line: ScheduleLine) -> tuple[bool, str]:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO schedule (
                        channel_id, subscription_id, utc_time_start, utc_time_end
                    ) VALUES (%s, %s, %s, %s)
                    RETURNING id, channel_id, subscription_id, utc_time_start, utc_time_end
                """, (line.channel_id, line.subscription_id, line.utc_time_start, line.utc_time_end))
                res = cursor.fetchone()
        except Error as e:
            return False, str(e)
        
        return True, ScheduleLine(*res)


    def get_schedule_for_usr(
        self,
        user_id: int,
        channel_name: str | None = None,
        channel_id: int | None = None,
        show_title: str | None = None,
        start_time: datetime | None = None):

        query = """
            SELECT
                channels.name AS channel_name,
                subscriptions.title AS show_title,
                schedule.utc_time_start + users.timezone::int * INTERVAL '1 hour' AS time_start,
                schedule.utc_time_end + users.timezone::int * INTERVAL '1 hour' AS time_end
            FROM schedule
            JOIN channels ON channels.id = schedule.channel_id
            JOIN subscriptions ON subscriptions.id = schedule.subscription_id
            JOIN users ON subscriptions.user_id = users.id
        """

        filters = ["users.id = %s"]
        args = [user_id]

        if show_title:
            filters.append("subscription.title = %s")
            args.append(show_title)
        
        if channel_name:
            filters.append("channel.name = %s")
            args.append(channel_name)
        
        if channel_id:
            filters.append("channel.id = %s")
            args.append(channel_id)
        

        if start_time:
            filters.append("schedule.utc_start_time >= %s")
            args.append(start_time)

        query += " WHERE " + " AND ".join(filters)

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, tuple(args))
                shows = cursor.fetchall()
        except Error as e:
            return False, str(e)

        return True, [Show(*show) for show in shows]



class SubscriptionRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

    def get_all(
        self,
        user_id: int | None = None,
        title: str | None = None
    ) -> tuple[bool, str | list[Subscription]]:

        query = """
            SELECT * FROM subscriptions
        """

        filters = []
        args = []

        if title:
            filters.append("title ILIKE %s")
            args.append(f"{title}%")

        if user_id:
            filters.append("user_id = %s")
            args.append(user_id)

        if filters:
            query += " WHERE " + " AND ".join(filters)

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, tuple(args))
                rows = cursor.fetchall()
        except Error as e:
            return False, str(e)
        
        return True, [Subscription(*row) for row in rows]


    async def get_by_user_id(self, user_id: int) -> tuple[bool, Union[list[Subscription], str]]:
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT id, user_id, title
                    FROM subscriptions
                    WHERE user_id=%s
                """, (user_id, ))
                rows = await cursor.fetchall()
        except Error as e:
            return False, str(e)

        return [Subscription(*row) for row in rows]


    async def add(self, subscription: Subscription):
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO subscriptions (user_id, title)
                    VALUES (%s, %s)
                    RETURNING id
                """, (subscription.user_id, subscription.title))
                obj = await cursor.fetchone()
                subscription.id = obj[0]
        except Error as e:
            return False, str(e)
        
        return True, subscription


    async def remove(self, subscription: Subscription):
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    DELETE FROM subscriptions
                    WHERE user_id=%s AND title=%s
                    RETURNING id
                """, (subscription.user_id, subscription.title))
                obj = await cursor.fetchone()
                subscription.id = obj[0]
        except Error as e:
            return False, str(e)
        
        return True, subscription
