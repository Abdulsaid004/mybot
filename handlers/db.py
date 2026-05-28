import sqlite3
from datetime import datetime
from pathlib import Path

DB_NAME = "dealix.db"

def connect():
    return sqlite3.connect(DB_NAME)


def _column_exists(cur: sqlite3.Cursor, table_name: str, column_name: str) -> bool:
    cur.execute(f"PRAGMA table_info({table_name})")
    return any(row[1] == column_name for row in cur.fetchall())


def _ensure_column(cur: sqlite3.Cursor, table_name: str, column_name: str, definition: str):
    if not _column_exists(cur, table_name, column_name):
        cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def init_db():
    with connect() as con:
        cur = con.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                client_username TEXT,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                price TEXT,
                status TEXT NOT NULL DEFAULT 'new',
                executor_id INTEGER,
                executor_username TEXT,
                group_message_id INTEGER,
                created_at TEXT NOT NULL,
                final_file_type TEXT,
                final_file_id TEXT,
                commission_percent INTEGER DEFAULT 15,
                executor_payout INTEGER,
                platform_profit INTEGER,
                payout_status TEXT DEFAULT 'pending',
                executor_payment_info TEXT,
                executor_payment_status TEXT DEFAULT 'not_paid',
                materials_text TEXT DEFAULT '' 
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS order_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                file_type TEXT NOT NULL,
                file_id TEXT NOT NULL
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS draft_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                file_type TEXT NOT NULL,
                file_id TEXT NOT NULL
            )
            """
        )

        migrations = {
            "commission_percent": "INTEGER DEFAULT 15",
            "executor_payout": "INTEGER",
            "platform_profit": "INTEGER",
            "payout_status": "TEXT DEFAULT 'pending'",
            "executor_payment_info": "TEXT",
            "executor_payment_status": "TEXT DEFAULT 'not_paid'",
        }

        for column_name, definition in migrations.items():
            _ensure_column(cur, "orders", column_name, definition)

        con.commit()


def create_order(
    client_id: int,
    client_username: str | None,
    category: str,
    description: str,
    price: str | None,
):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO orders (
                client_id,
                client_username,
                category,
                description,
                price,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, 'waiting_executor', ?)
            """,
            (
                client_id,
                client_username,
                category,
                description,
                price,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        con.commit()
        return cur.lastrowid


def get_order(order_id: int):
    with connect() as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    
def update_order_materials(order_id: int, materials_text: str):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            "UPDATE orders SET materials_text = ? WHERE order_id = ?",
            (materials_text, order_id)
        )
        con.commit()    


def update_order_status(order_id: int, status: str):
    with connect() as con:
        cur = con.cursor()
        cur.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
        con.commit()


def set_group_message(order_id: int, group_message_id: int):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            UPDATE orders
            SET group_message_id = ?, status = 'published'
            WHERE order_id = ?
            """,
            (group_message_id, order_id),
        )
        con.commit()


def take_order(order_id: int, executor_id: int, executor_username: str | None):
    with connect() as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row = cur.fetchone()

        if not row:
            return False, "❌ Заказ не найден"

        if row["status"] != "waiting_executor":
            return False, "❌ Заказ уже занят"

        cur.execute(
            """
            UPDATE orders
            SET status = 'taken', executor_id = ?, executor_username = ?
            WHERE order_id = ? AND executor_id IS NULL AND status = 'waiting_executor'
            """,
            (executor_id, executor_username, order_id),
        )
        con.commit()

        if cur.rowcount == 0:
            return False, "❌ Кто-то уже взял этот заказ"

        return True, "✅ Заказ взят"


def get_executor_active_order(executor_id: int):
    with connect() as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            """
            SELECT * FROM orders
            WHERE executor_id = ? AND status IN ('taken', 'in_work', 'revision')
            ORDER BY order_id DESC LIMIT 1
            """,
            (executor_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def add_order_file(order_id: int, file_type: str, file_id: str):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO order_files (order_id, file_type, file_id)
            VALUES (?, ?, ?)
            """,
            (order_id, file_type, file_id),
        )
        con.commit()


def get_order_files(order_id: int):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            "SELECT file_type, file_id FROM order_files WHERE order_id = ?",
            (order_id,),
        )
        return cur.fetchall()


def delete_order_files(order_id: int):
    with connect() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM order_files WHERE order_id = ?", (order_id,))
        con.commit()


def add_draft_file(client_id: int, file_type: str, file_id: str):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO draft_files (client_id, file_type, file_id)
            VALUES (?, ?, ?)
            """,
            (client_id, file_type, file_id),
        )
        con.commit()


def move_draft_files_to_order(client_id: int, order_id: int):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            "SELECT file_type, file_id FROM draft_files WHERE client_id = ?",
            (client_id,),
        )
        files = cur.fetchall()

        for file_type, file_id in files:
            cur.execute(
                """
                INSERT INTO order_files (order_id, file_type, file_id)
                VALUES (?, ?, ?)
                """,
                (order_id, file_type, file_id),
            )

        cur.execute("DELETE FROM draft_files WHERE client_id = ?", (client_id,))
        con.commit()


def save_final_file(order_id: int, file_type: str, file_id: str):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            UPDATE orders
            SET final_file_type = ?, final_file_id = ?
            WHERE order_id = ?
            """,
            (file_type, file_id, order_id),
        )
        con.commit()


def get_final_file(order_id: int):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            SELECT final_file_type, final_file_id
            FROM orders
            WHERE order_id = ?
            """,
            (order_id,),
        )
        row = cur.fetchone()

        if not row or not row[0] or not row[1]:
            return None

        return {
            "file_type": row[0],
            "file_id": row[1],
        }


def save_executor_payment_info(order_id: int, payment_info: str):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            UPDATE orders
            SET executor_payment_info = ?
            WHERE order_id = ?
            """,
            (payment_info, order_id),
        )
        con.commit()
