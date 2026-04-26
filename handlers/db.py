import aiosqlite # type: ignore
import os

DB_PATH = "/data/dealix.db" if os.path.exists("/data") else "dealix.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            service TEXT,
            text TEXT,
            status TEXT,
            executor_id INTEGER,
            executor_username TEXT,
            group_message_id INTEGER
        )
        """)
        await db.commit()


async def create_order(user_id, username, service, text):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
        INSERT INTO orders (user_id, username, service, text, status)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, service, text, "published"))
        await db.commit()
        return cursor.lastrowid


async def update_order_taken(order_id, executor_id, executor_username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        UPDATE orders
        SET status = ?, executor_id = ?, executor_username = ?
        WHERE id = ?
        """, ("taken", executor_id, executor_username, order_id))
        await db.commit()


async def save_group_message_id(order_id, message_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        UPDATE orders
        SET group_message_id = ?
        WHERE id = ?
        """, (message_id, order_id))
        await db.commit()

