import sqlite3
import os
from datetime import date

# файл БД будет в корне проекта лежать
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tracker.db")


def init_db():
    # создаем файлик
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
    conn.commit()
    conn.close()


def save_to_db(time_per_app):
    # записуем время в базу данных
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