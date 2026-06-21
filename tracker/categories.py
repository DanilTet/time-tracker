import json
import os

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "..", "categories.json")
DEFAULT_CATEGORY = "Без категории"


def load_categories():
    if not os.path.exists(CATEGORIES_PATH):
        return {}
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_categories(categories):
    with open(CATEGORIES_PATH, "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)


def get_category(app_name, categories=None):
    if categories is None:
        categories = load_categories()
    return categories.get(app_name, DEFAULT_CATEGORY)


def set_category(app_name, category):
    # присвоить категорию
    categories = load_categories()
    categories[app_name] = category
    save_categories(categories)