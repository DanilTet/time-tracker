import json
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 5500
browser_status = {"domain": None, "audible": False}

class Handler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors_headers()
        self.end_headers()

    def do_POST(self):
        if self.path == "/update":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                browser_status["domain"] = data.get("domain")
                browser_status["audible"] = bool(data.get("audible", False))
            except Exception:
                pass

        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def log_message(self, format, *args):
        pass  # отключаем стандартные логи сервера


def get_browser_status():
    return browser_status["domain"], browser_status["audible"]


def run_server():
    server = HTTPServer(("localhost", PORT), Handler)
    print(f"[сервер расширения запущен на http://localhost:{PORT}]")
    server.serve_forever()