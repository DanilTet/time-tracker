import sqlite3
import os
from datetime import date, datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tracker.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_usage (
            date TEXT NOT NULL,
            app_name TEXT NOT NULL,
            seconds INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (date, app_name)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_usage_hourly (
            date TEXT NOT NULL,
            hour INTEGER NOT NULL,
            app_name TEXT NOT NULL,
            seconds INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (date, hour, app_name)
        )
    """)
    conn.commit()
    conn.close()


def save_to_db(time_per_app):
    if not time_per_app:
        return

    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for app_name, seconds in time_per_app.items():
        cursor.execute("""
            INSERT INTO app_usage (date, app_name, seconds)
            VALUES (?, ?, ?)
            ON CONFLICT(date, app_name) DO UPDATE SET seconds = seconds + excluded.seconds
        """, (today, app_name, seconds))

    conn.commit()
    conn.close()


def save_hourly_to_db(time_per_app):
    """То же самое, что save_to_db, но с привязкой к текущему часу.
    Окно накопления маленькое (~10 сек), поэтому переход через границу часа
    практически не встречается — этим можно спокойно пренебречь."""
    if not time_per_app:
        return

    now = datetime.now()
    today = now.date().isoformat()
    hour = now.hour

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for app_name, seconds in time_per_app.items():
        cursor.execute("""
            INSERT INTO app_usage_hourly (date, hour, app_name, seconds)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(date, hour, app_name) DO UPDATE SET seconds = seconds + excluded.seconds
        """, (today, hour, app_name, seconds))

    conn.commit()
    conn.close()


def get_usage_between(date_from, date_to):
    """Сумма секунд по каждой программе/сайту за период [date_from, date_to]."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT app_name, SUM(seconds) as total_seconds
        FROM app_usage
        WHERE date BETWEEN ? AND ?
        GROUP BY app_name
        ORDER BY total_seconds DESC
    """, (date_from, date_to))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_daily_rows(date_from, date_to):
    """Все строки (date, app_name, seconds) за период — для тепловой карты."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, app_name, seconds
        FROM app_usage
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    """, (date_from, date_to))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_hourly_rows(date_str):
    """Все строки (hour, app_name, seconds) за конкретный день — для таймлайна по часам."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT hour, app_name, seconds
        FROM app_usage_hourly
        WHERE date = ?
        ORDER BY hour
    """, (date_str,))
    rows = cursor.fetchall()
    conn.close()
    return rows