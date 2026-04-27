import os
import aiosqlite  # type: ignore

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
    await init_db()

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
        INSERT INTO orders (user_id, username, service, text, status)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, service, text, "waiting_payment"))

        await db.commit()
        return cursor.lastrowid

