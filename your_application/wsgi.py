from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs

import mvp_pos_insight_bot as bot
from web_app import HTML, build_state

DATA_DIR = os.getenv("DATA_DIR", "./data")
CONFIG_PATH = os.getenv("ACCOUNT_CONFIG", "./data/sample_account.json")

_account, _rows, _metrics = build_state(DATA_DIR, CONFIG_PATH if Path(CONFIG_PATH).exists() else None)


def _json(start_response, payload: dict, status: str = "200 OK") -> list[bytes]:
    body = json.dumps(payload).encode("utf-8")
    start_response(status, [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(body))),
    ])
    return [body]


def application(environ, start_response) -> Iterable[bytes]:
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")

    if method == "GET" and path == "/healthz":
        return _json(start_response, {
            "ok": True,
            "service": "ai-store-assistant-mvp",
            "render_git_commit": os.getenv("RENDER_GIT_COMMIT", "unknown"),
            "render_service_id": os.getenv("RENDER_SERVICE_ID", "unknown"),
        })

    if method == "GET" and (path == "/" or path.startswith("/index")):
        body = HTML.encode("utf-8")
        start_response("200 OK", [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ])
        return [body]

    if method == "POST" and path == "/api/chat":
        try:
            length = int(environ.get("CONTENT_LENGTH") or "0")
        except ValueError:
            length = 0
        raw = environ.get("wsgi.input").read(length) if length else b""
        payload = {}
        if raw:
            payload = json.loads(raw.decode("utf-8"))
        elif environ.get("QUERY_STRING"):
            payload = {k: v[0] for k, v in parse_qs(environ["QUERY_STRING"]).items()}
        q = str(payload.get("q", "")).strip()
        if not q:
            return _json(start_response, {"answer": "Please ask a question."}, "400 Bad Request")

        answer = bot.respond(q, _metrics, _rows, str(_account["bot_name"]))
        return _json(start_response, {"answer": answer})

    return _json(start_response, {"error": "Not Found"}, "404 Not Found")
