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
    body{font-family:Arial,sans-serif;max-width:1100px;margin:20px auto;padding:0 12px}
    .layout{display:grid;grid-template-columns:1.1fr 0.9fr;gap:16px}
    .panel{border:1px solid #ddd;border-radius:10px;padding:12px;background:#fff}
    .chat{border:1px solid #ddd;border-radius:8px;padding:12px;height:380px;overflow:auto;background:#fafafa}
    .msg{margin:10px 0;padding:8px 10px;border-radius:8px;max-width:90%;white-space:pre-wrap}
    .you{background:#dff1ff;margin-left:auto}
    .bot{background:#ececec}
    .row{display:flex;gap:8px;margin-top:10px;align-items:center}
    input{flex:1;padding:10px}
    button{padding:10px 14px;border:1px solid #bbb;border-radius:6px;background:#fff;cursor:pointer}
    button:hover{background:#f5f5f5}
    .hint{color:#666;font-size:13px;margin-bottom:6px}
    .status{font-size:12px;color:#555;min-height:16px;margin-top:6px}
    .kpis{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-bottom:10px}
    .kpi{background:#f7f7f9;border:1px solid #ececf0;border-radius:8px;padding:8px}
    .kpi .label{font-size:12px;color:#666}
    .kpi .value{font-weight:700;margin-top:4px}
    table{width:100%;border-collapse:collapse;font-size:13px}
    th,td{border-bottom:1px solid #eee;padding:6px;text-align:left}
    @media (max-width:900px){.layout{grid-template-columns:1fr}}
  </style>
</head>
<body>
  <h2>AI Store Assistant (MVP)</h2>
  <div class='hint'>Trust-building mode: ask AI + verify with dashboard numbers side-by-side.</div>
  <div class='layout'>
    <section class='panel'>
      <div class='hint'>Try: <code>what is my status today?</code>, <code>stores</code>, <code>show store tea-001 status</code>, <code>table</code>, <code>diagram</code>, <code>sms</code></div>
      <div class='hint'>Voice: click 🎤 to speak your question, and click 🔊 to enable bot voice replies.</div>
      <div id='chat' class='chat'></div>
      <div class='row'>
        <input id='q' placeholder='Ask your store assistant...'/>
        <button onclick='send()'>Send</button>
        <button onclick='startVoiceInput()' title='Speak your message'>🎤 Speak</button>
        <button id='ttsBtn' onclick='toggleVoiceReply()' title='Toggle voice replies'>🔊 Voice Reply: Off</button>
      </div>
      <div id='status' class='status'></div>
    </section>

    <section class='panel'>
      <div class='row' style='margin-top:0'>
        <strong>Owner Dashboard (numbers view)</strong>
        <button style='margin-left:auto' onclick='loadDashboard()'>Refresh</button>
      </div>
      <div class='hint'>Use this panel to verify the exact metrics behind AI answers.</div>
      <div id='kpis' class='kpis'></div>
      <table>
        <thead>
          <tr>
            <th>Store</th>
            <th>Revenue</th>
            <th>Orders</th>
            <th>Avg Order</th>
            <th>Labor %</th>
            <th>Waste %</th>
          </tr>
        </thead>
        <tbody id='storeRows'></tbody>
      </table>
    </section>
  </div>
<script>
const chat = document.getElementById('chat');
const statusEl = document.getElementById('status');
const ttsBtn = document.getElementById('ttsBtn');
let voiceReplyEnabled = false;

function setStatus(text){ statusEl.textContent = text; }
function money(n){ return '$'+Number(n||0).toFixed(2); }
function pct(n){ return Number(n||0).toFixed(1)+'%'; }

function add(text, cls){
  const d = document.createElement('div');
  d.className='msg '+cls;
  d.textContent=text;
  chat.appendChild(d);
  chat.scrollTop = chat.scrollHeight;
}

function speak(text){
  if(!voiceReplyEnabled || !('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate = 1;
  utter.pitch = 1;
  window.speechSynthesis.speak(utter);
}

function toggleVoiceReply(){
  voiceReplyEnabled = !voiceReplyEnabled;
  ttsBtn.textContent = voiceReplyEnabled ? '🔊 Voice Reply: On' : '🔊 Voice Reply: Off';
  setStatus(voiceReplyEnabled ? 'Voice replies enabled.' : 'Voice replies disabled.');
}

async function send(prefilledQ){
  const qInput = document.getElementById('q');
  const q = (prefilledQ || qInput.value).trim();
  if(!q) return;
  add(q, 'you');
  qInput.value='';
  setStatus('Thinking...');
  const r = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({q})});
  const data = await r.json();
  add(data.answer, 'bot');
  speak(data.answer);
  setStatus('Ready.');
}

function startVoiceInput(){
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SpeechRecognition){
    setStatus('Voice input is not supported by this browser.');
    return;
  }
  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  setStatus('Listening... please speak now.');
  recognition.onresult = function(event){
    const transcript = event.results[0][0].transcript || '';
    document.getElementById('q').value = transcript;
    setStatus('Voice captured. Sending...');
    send(transcript);
  };
  recognition.onerror = function(event){ setStatus('Voice input error: ' + event.error); };
  recognition.onend = function(){ if(statusEl.textContent.startsWith('Listening')) setStatus('Listening stopped.'); };
  recognition.start();
}

async function loadDashboard(){
  const r = await fetch('/api/dashboard');
  const data = await r.json();

  const kpis = document.getElementById('kpis');
  const s = data.summary || {};
  kpis.innerHTML = '';
  [
    ['Total Revenue', money(s.revenue)],
    ['Total Orders', String(s.orders || 0)],
    ['Avg Order', money(s.avg_order)],
    ['Labor Ratio', pct(s.labor_ratio)],
    ['Waste Ratio', pct(s.waste_ratio)],
    ['Top Item', String(s.top_item || 'n/a')],
  ].forEach(([label, value]) => {
    const d = document.createElement('div');
    d.className = 'kpi';
    d.innerHTML = `<div class='label'>${label}</div><div class='value'>${value}</div>`;
    kpis.appendChild(d);
  });

  const body = document.getElementById('storeRows');
  body.innerHTML = '';
  (data.stores || []).forEach((row) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${row.store_id}</td><td>${money(row.revenue)}</td><td>${row.orders}</td><td>${money(row.avg_order)}</td><td>${pct(row.labor_ratio)}</td><td>${pct(row.waste_ratio)}</td>`;
    body.appendChild(tr);
  });
}

window.addEventListener('keydown', (e)=>{ if(e.key==='Enter') send();});
add('Assistant ready. Ask: what is my status today?', 'bot');
setStatus('Ready.');
loadDashboard();
</script>
</body>
</html>
"""


def build_state(data_dir: str, config: str | None):
    account = bot.load_account_config(config)
    rows = bot.normalize(bot.load_rows(data_dir))
    metrics = bot.metrics(rows)
    return account, rows, metrics


def dashboard_payload(rows: list[dict[str, object]], metrics: dict[str, object]) -> dict:
    store_map = bot.store_metrics_map(rows)
    stores = []
    for store_id, sm in store_map.items():
        stores.append({
            "store_id": store_id,
            "revenue": round(float(sm.get("revenue", 0.0)), 2),
            "orders": int(sm.get("orders", 0)),
            "avg_order": round(float(sm.get("avg_order", 0.0)), 2),
            "labor_ratio": round(float(sm.get("labor_ratio", 0.0)), 2),
            "waste_ratio": round(float(sm.get("waste_ratio", 0.0)), 2),
        })
    stores.sort(key=lambda x: x["revenue"], reverse=True)

    summary = {
        "revenue": round(float(metrics.get("revenue", 0.0)), 2),
        "orders": int(metrics.get("orders", 0)),
        "avg_order": round(float(metrics.get("avg_order", 0.0)), 2),
        "labor_ratio": round(float(metrics.get("labor_ratio", 0.0)), 2),
        "waste_ratio": round(float(metrics.get("waste_ratio", 0.0)), 2),
        "top_item": str(metrics.get("top_item", "n/a")),
    }
    return {"summary": summary, "stores": stores}


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
        if self.path == '/api/dashboard':
            self._json(dashboard_payload(self.rows, self.metrics))
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
