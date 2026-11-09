#!/usr/bin/env python3
"""本地预览用 mock 后端：把 frontend/dist 当静态站点，API 返回默认配置。

用途：没有 Go 环境时，验证前端界面改动（重构前后截图比对）。

    python tools/mock_server.py --port 23100
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "frontend" / "dist"
DEFAULT_JSON = ROOT / "backend" / "config" / "default.json"

APP_DATA = json.loads(DEFAULT_JSON.read_text(encoding="utf-8-sig"))


def _json(payload: dict) -> tuple[int, str, bytes]:
    return 200, "application/json", json.dumps(payload, ensure_ascii=False).encode()


ROUTES = {
    "/api/data": lambda: _json(APP_DATA),
    "/api/system-config": lambda: _json({"authMode": "single", "enableDocker": False}),
    "/api/version": lambda: _json({"version": APP_DATA.get("version", 1), "latest": "1.2.6"}),
    "/api/ip": lambda: _json({"ip": "192.168.1.10", "country": "中国", "province": "天津"}),
    "/api/docker-status": lambda: _json({"enabled": False}),
    "/api/config/proxy-status": lambda: _json({"enabled": False}),
    "/api/rtt": lambda: _json({"rtt": 2}),
    "/api/ping": lambda: _json({"ok": True}),
    "/api/hot": lambda: _json({"weibo": [], "zhihu": [], "baidu": [], "bilibili": []}),
    "/api/rss": lambda: _json({"items": []}),
    "/api/rss/meta": lambda: _json({"items": []}),
    "/api/weather": lambda: _json({"temp": 20, "text": "晴", "city": "天津"}),
    "/api/music-list": lambda: _json({"files": []}),
    "/api/backgrounds": lambda: _json({"files": []}),
    "/api/mobile_backgrounds": lambda: _json({"files": []}),
    "/api/ali-icons": lambda: _json({"icons": []}),
    "/api/custom-scripts": lambda: _json({}),
    "/api/config-versions": lambda: _json({"versions": []}),
    "/api/login": lambda: _json({"token": "mock-token", "username": "admin"}),
    "/api/save": lambda: _json({"version": APP_DATA.get("version", 1) + 1}),
    "/api/socket.io/": lambda: _json({"ok": True}),
}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def log_message(self, fmt, *args):  # 静音
        pass

    def _answer(self) -> bool:
        path = self.path.split("?")[0]
        route = ROUTES.get(path)
        if route:
            code, ctype, body = route()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return True
        if path.startswith("/api/"):
            code, ctype, body = _json({})
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return True
        return False

    def do_GET(self):  # noqa: N802
        if self._answer():
            return
        super().do_GET()

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        if not self._answer():
            self.send_error(404)

    def do_PUT(self):  # noqa: N802
        self.do_POST()

    def do_DELETE(self):  # noqa: N802
        if not self._answer():
            self.send_error(404)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=23100)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("text/css", ".css")
    if not (DIST / "index.html").exists():
        raise SystemExit(f"缺少构建产物：{DIST}，先跑 npm run build-only")
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"mock backend on http://{args.host}:{args.port}  (dist={DIST})")
    srv.serve_forever()


if __name__ == "__main__":
    main()
