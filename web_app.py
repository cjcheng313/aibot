#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import mvp_pos_insight_bot as bot


HTML = """<!doctype html>
<html>
<head>
  <meta charset='utf-8'/>
  <meta name='viewport' content='width=device-width, initial-scale=1'/>
  <title>AI Store Assistant MVP</title>
  <style>
    body{font-family:Arial,sans-serif;max-width:900px;margin:20px auto;padding:0 12px}
    .chat{border:1px solid #ddd;border-radius:8px;padding:12px;height:420px;overflow:auto;background:#fafafa}
    .msg{margin:10px 0;padding:8px 10px;border-radius:8px;max-width:80%}
    .you{background:#dff1ff;margin-left:auto}
    .bot{background:#ececec}
    .row{display:flex;gap:8px;margin-top:10px}
    input{flex:1;padding:10px}
    button{padding:10px 14px}
    .hint{color:#666;font-size:13px}
  </style>
</head>
<body>
  <h2>AI Store Assistant (MVP)</h2>
  <div class='hint'>Try: <code>what is my status today?</code>, <code>stores</code>, <code>show store tea-001 status</code>, <code>table</code>, <code>diagram</code>, <code>sms</code></div>
  <div id='chat' class='chat'></div>
  <div class='row'>
    <input id='q' placeholder='Ask your store assistant...'/>
    <button onclick='send()'>Send</button>
  </div>
<script>
const chat = document.getElementById('chat');
function add(text, cls){
  const d = document.createElement('div'); d.className='msg '+cls; d.textContent=text; chat.appendChild(d); chat.scrollTop = chat.scrollHeight;
}
async function send(){
  const q = document.getElementById('q').value.trim();
  if(!q) return;
  add(q, 'you');
  document.getElementById('q').value='';
  const r = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({q})});
  const data = await r.json();
  add(data.answer, 'bot');
}
window.addEventListener('keydown', (e)=>{ if(e.key==='Enter') send();});
add('Assistant ready. Ask: what is my status today?', 'bot');
</script>
</body>
</html>
"""


def build_state(data_dir: str, config: str | None):
    account = bot.load_account_config(config)
    rows = bot.normalize(bot.load_rows(data_dir))
    metrics = bot.metrics(rows)
    return account, rows, metrics


class Handler(BaseHTTPRequestHandler):
    account = None
    rows = None
    metrics = None

    def _json(self, payload: dict, code: int = 200):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/healthz':
            self._json({
                'ok': True,
                'service': 'ai-store-assistant-mvp',
                'render_git_commit': os.getenv('RENDER_GIT_COMMIT', 'unknown'),
                'render_service_id': os.getenv('RENDER_SERVICE_ID', 'unknown'),
            })
            return
        if self.path == '/' or self.path.startswith('/index'):
            content = HTML.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        self.send_error(404)

    def do_POST(self):
        if self.path != '/api/chat':
            self.send_error(404)
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            payload = json.loads(self.rfile.read(length) or b'{}')
            q = str(payload.get('q', '')).strip()
            if not q:
                self._json({'answer': 'Please ask a question.'}, 400)
                return
            answer = bot.respond(q, self.metrics, self.rows, str(self.account['bot_name']))
            self._json({'answer': answer})
        except Exception as exc:
            self._json({'answer': f'Error: {exc}'}, 500)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data-dir', default='./data')
    p.add_argument('--config', default='./data/sample_account.json')
    p.add_argument('--host', default='0.0.0.0')
    p.add_argument('--port', type=int, default=8000)
    args = p.parse_args()

    account, rows, metrics = build_state(args.data_dir, args.config if Path(args.config).exists() else None)
    Handler.account = account
    Handler.rows = rows
    Handler.metrics = metrics

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Serving on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == '__main__':
    main()
