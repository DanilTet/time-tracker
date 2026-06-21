import sqlite3
import os
from collections import defaultdict
from categories import load_categories, get_category

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tracker.db")


def show_today():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT app_name, seconds FROM app_usage WHERE date = date('now')")
    rows = cursor.fetchall()
    conn.close()

    categories = load_categories()
    by_category = defaultdict(int)
    by_app = defaultdict(int)

    for app_name, seconds in rows:
        category = get_category(app_name, categories)
        by_category[category] += seconds
        by_app[app_name] += seconds

    print("=== По категориям ===")
    for category, seconds in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"{category}: {seconds // 60} мин {seconds % 60} сек")

    print("\n=== По приложениям/сайтам ===")
    for app_name, seconds in sorted(by_app.items(), key=lambda x: -x[1]):
        cat = get_category(app_name, categories)
        print(f"{app_name} [{cat}]: {seconds // 60} мин {seconds % 60} сек")


if __name__ == "__main__":
    show_today()