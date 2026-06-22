import json
import os

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "..", "categories.json")
LIMITS_PATH = os.path.join(os.path.dirname(__file__), "..", "category_limits.json")
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
    categories = load_categories()
    categories[app_name] = category
    save_categories(categories)


def load_limits():
    if not os.path.exists(LIMITS_PATH):
        return {}
    with open(LIMITS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_limits(limits):
    with open(LIMITS_PATH, "w", encoding="utf-8") as f:
        json.dump(limits, f, ensure_ascii=False, indent=2)


def set_limit(category, seconds):
    """seconds=None — категория существует (видна в списках), но лимит не задан."""
    limits = load_limits()
    limits[category] = seconds
    save_limits(limits)


def rename_category(old_name, new_name):
    if old_name == new_name:
        return

    categories = load_categories()
    changed = False
    for app, cat in categories.items():
        if cat == old_name:
            categories[app] = new_name
            changed = True
    if changed:
        save_categories(categories)

    limits = load_limits()
    if old_name in limits:
        limits[new_name] = limits.pop(old_name)
        save_limits(limits)


def delete_category(category):
    """Приложения, которые были в этой категории, становятся DEFAULT_CATEGORY."""
    categories = load_categories()
    changed = False
    for app, cat in list(categories.items()):
        if cat == category:
            categories[app] = DEFAULT_CATEGORY
            changed = True
    if changed:
        save_categories(categories)

    limits = load_limits()
    if category in limits:
        limits.pop(category)
        save_limits(limits)