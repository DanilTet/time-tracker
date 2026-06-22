import json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from db import get_usage_between, get_daily_rows, get_hourly_rows
from categories import (
    load_categories, set_category, DEFAULT_CATEGORY,
    load_limits, set_limit, rename_category, delete_category
)

PORT = 5500
browser_status = {"domain": None, "audible": False}


class Handler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/api/stats":
            date_from = params.get("from", [None])[0]
            date_to = params.get("to", [None])[0]
            if not date_from or not date_to:
                self._send_json({"error": "нужны параметры from и to"}, 400)
                return

            rows = get_usage_between(date_from, date_to)
            categories = load_categories()

            by_app = []
            by_category = {}

            for app_name, seconds in rows:
                category = categories.get(app_name, DEFAULT_CATEGORY)
                by_app.append({"app_name": app_name, "seconds": seconds, "category": category})
                by_category[category] = by_category.get(category, 0) + seconds

            self._send_json({"by_app": by_app, "by_category": by_category})
            return

        if parsed.path == "/api/daily":
            date_from = params.get("from", [None])[0]
            date_to = params.get("to", [None])[0]
            if not date_from or not date_to:
                self._send_json({"error": "нужны параметры from и to"}, 400)
                return

            rows = get_daily_rows(date_from, date_to)
            categories = load_categories()

            by_date = {}
            for d, app_name, seconds in rows:
                entry = by_date.setdefault(d, {"total": 0, "by_category": {}})
                entry["total"] += seconds
                category = categories.get(app_name, DEFAULT_CATEGORY)
                entry["by_category"][category] = entry["by_category"].get(category, 0) + seconds

            self._send_json(by_date)
            return

        if parsed.path == "/api/hourly":
            date_str = params.get("date", [None])[0]
            if not date_str:
                self._send_json({"error": "нужен параметр date"}, 400)
                return

            rows = get_hourly_rows(date_str)
            categories = load_categories()

            hours = {}
            for hour, app_name, seconds in rows:
                entry = hours.setdefault(str(hour), {"total": 0, "by_category": {}, "by_app": {}})
                entry["total"] += seconds
                category = categories.get(app_name, DEFAULT_CATEGORY)
                entry["by_category"][category] = entry["by_category"].get(category, 0) + seconds
                entry["by_app"][app_name] = entry["by_app"].get(app_name, 0) + seconds

            self._send_json(hours)
            return

        if parsed.path == "/api/categories":
            categories = load_categories()
            limits = load_limits()
            known = sorted(set(categories.values()) | set(limits.keys()) | {DEFAULT_CATEGORY})
            self._send_json({"mapping": categories, "known_categories": known})
            return

        if parsed.path == "/api/category-limits":
            self._send_json({"limits": load_limits()})
            return

        self.send_response(404)
        self._set_cors_headers()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        if self.path == "/update":
            try:
                data = json.loads(body)
                browser_status["domain"] = data.get("domain")
                browser_status["audible"] = bool(data.get("audible", False))
            except Exception:
                pass
            self.send_response(200)
            self._set_cors_headers()
            self.end_headers()
            return

        if self.path == "/api/categories":
            try:
                data = json.loads(body)
                app_name = data.get("app_name")
                category = data.get("category")
                if app_name and category:
                    set_category(app_name, category)
                    self._send_json({"ok": True})
                else:
                    self._send_json({"error": "нужны app_name и category"}, 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 400)
            return

        if self.path == "/api/category-limits":
            try:
                data = json.loads(body)
                category = data.get("category")
                limit_seconds = data.get("limit_seconds")
                if not category:
                    self._send_json({"error": "нужен category"}, 400)
                    return
                set_limit(category, limit_seconds)
                self._send_json({"ok": True})
            except Exception as e:
                self._send_json({"error": str(e)}, 400)
            return

        if self.path == "/api/categories/rename":
            try:
                data = json.loads(body)
                old_name = data.get("old_name")
                new_name = data.get("new_name")
                if not old_name or not new_name:
                    self._send_json({"error": "нужны old_name и new_name"}, 400)
                    return
                if old_name == DEFAULT_CATEGORY:
                    self._send_json({"error": "нельзя переименовать системную категорию"}, 400)
                    return
                rename_category(old_name, new_name)
                self._send_json({"ok": True})
            except Exception as e:
                self._send_json({"error": str(e)}, 400)
            return

        if self.path == "/api/categories/delete":
            try:
                data = json.loads(body)
                category = data.get("category")
                if not category:
                    self._send_json({"error": "нужен category"}, 400)
                    return
                if category == DEFAULT_CATEGORY:
                    self._send_json({"error": "нельзя удалить системную категорию"}, 400)
                    return
                delete_category(category)
                self._send_json({"ok": True})
            except Exception as e:
                self._send_json({"error": str(e)}, 400)
            return

        self.send_response(404)
        self._set_cors_headers()
        self.end_headers()

    def log_message(self, format, *args):
        pass


def get_browser_status():
    return browser_status["domain"], browser_status["audible"]


def run_server():
    server = ThreadingHTTPServer(("localhost", PORT), Handler)
    print(f"[сервер расширения запущен на http://localhost:{PORT}]")
    server.serve_forever()