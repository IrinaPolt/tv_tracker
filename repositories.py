from typing import Union

from psycopg import Connection, Error

from models import User, Subscription



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


class SubscriptionRepository:
    def __init__(self, connection: Connection):
        self.connection = connection


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
