import json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from db import get_usage_between, get_daily_rows, get_hourly_rows
from categories import load_categories, set_category, DEFAULT_CATEGORY

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
            known = sorted(set(categories.values()) | {DEFAULT_CATEGORY})
            self._send_json({"mapping": categories, "known_categories": known})
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