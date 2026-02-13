#!/usr/bin/env python3
"""MVP POS Insight Bot (stdlib-only).

Now includes:
- multi-store rollup and per-store drill-down
- owner account config (bot name + store list)
- SMS brief formatter
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional


DEFAULT_BOT_NAME = "Nomi"


def _match_col(cols: List[str], candidates: List[str]) -> Optional[str]:
    lower_map = {c.lower().strip(): c for c in cols}
    for key in candidates:
        if key in lower_map:
            return lower_map[key]
    for c in cols:
        cl = c.lower().strip()
        for key in candidates:
            if key in cl:
                return c
    return None


def _to_float(v: str) -> float:
    try:
        return float(str(v).replace(",", "").strip())
    except Exception:
        return 0.0


def load_account_config(config_path: Optional[str]) -> Dict[str, object]:
    if not config_path:
        return {"owner_name": "Owner", "bot_name": DEFAULT_BOT_NAME, "stores": []}
    with open(config_path, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    return {
        "owner_name": cfg.get("owner_name", "Owner"),
        "bot_name": cfg.get("bot_name", DEFAULT_BOT_NAME),
        "stores": cfg.get("stores", []),
    }


def load_rows(data_dir: str) -> List[Dict[str, str]]:
    files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")

    rows: List[Dict[str, str]] = []
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for r in reader:
                r["_source_file"] = os.path.basename(f)
                rows.append(r)
    return rows


def normalize(rows: List[Dict[str, str]]) -> List[Dict[str, object]]:
    if not rows:
        return []
    cols = list(rows[0].keys())

    date_col = _match_col(cols, ["date", "business_date", "day", "transaction_date"])
    rev_col = _match_col(cols, ["revenue", "sales", "net_sales", "total_sales", "amount"])
    qty_col = _match_col(cols, ["quantity", "qty", "items"])
    labor_col = _match_col(cols, ["labor_cost", "labor", "staff_cost", "payroll"])
    waste_col = _match_col(cols, ["waste", "waste_cost", "spoilage"])
    item_col = _match_col(cols, ["item", "menu_item", "product", "sku"])
    order_col = _match_col(cols, ["order_id", "ticket_id", "check_id", "receipt_id"])
    store_col = _match_col(cols, ["store_id", "location_id", "store", "location"])

    out: List[Dict[str, object]] = []
    for i, r in enumerate(rows):
        d = None
        if date_col and r.get(date_col):
            try:
                d = datetime.fromisoformat(str(r[date_col])[:10]).date()
            except Exception:
                d = None

        out.append(
            {
                "date": d,
                "store_id": str(r.get(store_col, "default-store") or "default-store") if store_col else "default-store",
                "revenue": _to_float(r.get(rev_col, "0")) if rev_col else 0.0,
                "quantity": _to_float(r.get(qty_col, "1")) if qty_col else 1.0,
                "labor_cost": _to_float(r.get(labor_col, "0")) if labor_col else 0.0,
                "waste_cost": _to_float(r.get(waste_col, "0")) if waste_col else 0.0,
                "item_name": str(r.get(item_col, "unknown")) if item_col else "unknown",
                "order_key": str(r.get(order_col, i)) if order_col else str(i),
            }
        )
    return out


def metrics(rows: List[Dict[str, object]]) -> Dict[str, object]:
    revenue = sum(float(r["revenue"]) for r in rows)
    orders = len(set(str(r["order_key"]) for r in rows))
    avg_order = revenue / orders if orders else 0.0
    labor = sum(float(r["labor_cost"]) for r in rows)
    waste = sum(float(r["waste_cost"]) for r in rows)
    labor_ratio = (labor / revenue * 100) if revenue else 0.0
    waste_ratio = (waste / revenue * 100) if revenue else 0.0

    item_sales: Dict[str, float] = defaultdict(float)
    for r in rows:
        item_sales[str(r["item_name"])] += float(r["revenue"])
    top_item = "n/a"
    top_sales = 0.0
    if item_sales:
        top_item, top_sales = max(item_sales.items(), key=lambda x: x[1])

    return {
        "revenue": revenue,
        "orders": orders,
        "avg_order": avg_order,
        "labor": labor,
        "waste": waste,
        "labor_ratio": labor_ratio,
        "waste_ratio": waste_ratio,
        "top_item": top_item,
        "top_sales": top_sales,
    }


def store_metrics_map(rows: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    grouped: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for r in rows:
        grouped[str(r["store_id"])].append(r)
    return {store_id: metrics(store_rows) for store_id, store_rows in grouped.items()}


def top_action(m: Dict[str, object]) -> str:
    if m["labor_ratio"] > 30:
        return "Labor ratio is high. Review shift overlap and overtime today."
    if m["waste_ratio"] > 5:
        return "Waste is high. Reduce prep volume for low-demand windows."
    if m["avg_order"] < 15:
        return "Average order is low. Test bundle/upsell prompts."
    return "KPIs look stable. Keep monitoring daily trend and item mix."


def summary(m: Dict[str, object], scope: str = "all stores") -> str:
    return (
        f"Status ({scope}): Revenue ${m['revenue']:,.2f} from {m['orders']} orders. "
        f"Avg order ${m['avg_order']:,.2f}. Labor ratio {m['labor_ratio']:.1f}%. "
        f"Waste ratio {m['waste_ratio']:.1f}%. Top item: {m['top_item']} (${m['top_sales']:,.2f}).\n"
        f"Top action: {top_action(m)}"
    )


def sms_brief(m: Dict[str, object], bot_name: str) -> str:
    return (
        f"{bot_name}: Revenue ${m['revenue']:,.0f}; Labor {m['labor_ratio']:.1f}%; "
        f"Waste {m['waste_ratio']:.1f}%. Action: {top_action(m)}"
    )


def daily_table(rows: List[Dict[str, object]]) -> str:
    by_day: Dict[object, Dict[str, float]] = defaultdict(lambda: {"revenue": 0.0, "labor": 0.0, "waste": 0.0})
    orders_by_day: Dict[object, set] = defaultdict(set)

    for r in rows:
        d = r["date"]
        if d is None:
            continue
        by_day[d]["revenue"] += float(r["revenue"])
        by_day[d]["labor"] += float(r["labor_cost"])
        by_day[d]["waste"] += float(r["waste_cost"])
        orders_by_day[d].add(str(r["order_key"]))

    if not by_day:
        return "No valid date column detected in CSVs."

    lines = ["date        revenue   orders  avg_order labor   waste"]
    for d in sorted(by_day.keys()):
        orders = len(orders_by_day[d])
        rev = by_day[d]["revenue"]
        avg = rev / orders if orders else 0.0
        lines.append(f"{d}  {rev:8.2f} {orders:7d} {avg:9.2f} {by_day[d]['labor']:7.2f} {by_day[d]['waste']:7.2f}")
    return "\n".join(lines)


def diagram(m: Dict[str, object]) -> str:
    def bar(pct: float) -> str:
        n = max(0, min(20, int(round(pct / 5))))
        return "█" * n + "░" * (20 - n)

    return (
        "Cost Ratios vs Revenue\n"
        f"Labor {m['labor_ratio']:5.1f}% |{bar(float(m['labor_ratio']))}|\n"
        f"Waste {m['waste_ratio']:5.1f}% |{bar(float(m['waste_ratio']))}|"
    )


def _parse_store_request(q: str, store_ids: List[str]) -> Optional[str]:
    ql = q.lower()
    if "store" not in ql:
        return None
    for sid in store_ids:
        if sid.lower() in ql:
            return sid
    return None


def respond(q: str, m: Dict[str, object], rows: List[Dict[str, object]], bot_name: str) -> str:
    ql = q.lower()
    smap = store_metrics_map(rows)
    requested_store = _parse_store_request(q, list(smap.keys()))
    if requested_store:
        return summary(smap[requested_store], scope=f"store {requested_store}")

    if any(k in ql for k in ["status", "summary", "how did", "insight"]):
        return summary(m)
    if "labor" in ql:
        return f"Labor cost ${m['labor']:,.2f} ({m['labor_ratio']:.1f}% of revenue)."
    if "waste" in ql:
        return f"Waste cost ${m['waste']:,.2f} ({m['waste_ratio']:.1f}% of revenue)."
    if "top" in ql and "item" in ql:
        return f"Top item is {m['top_item']} at ${m['top_sales']:,.2f}."
    if "table" in ql or "detail" in ql:
        return "\n" + daily_table(rows)
    if "diagram" in ql or "chart" in ql:
        return "\n" + diagram(m)
    if "sms" in ql:
        return sms_brief(m, bot_name)
    if "stores" in ql:
        return "Known stores: " + ", ".join(sorted(smap.keys()))
    return "Ask me: status, store <id> status, labor, waste, top item, table, diagram, sms."


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", required=True)
    p.add_argument("--config", help="Path to owner account JSON config")
    p.add_argument("--no-chat", action="store_true")
    p.add_argument("--print-sms", action="store_true", help="Print SMS brief and exit")
    args = p.parse_args()

    account = load_account_config(args.config)
    rows = normalize(load_rows(args.data_dir))
    m = metrics(rows)

    if args.print_sms:
        print(sms_brief(m, str(account["bot_name"])))
        return

    bot_name = str(account["bot_name"])
    print(f"{bot_name}> {summary(m)}")

    if args.no_chat:
        return

    print(f"\n{bot_name} ready. Ask 'what is my status today?' (exit to quit)")
    while True:
        q = input("you> ").strip()
        if q.lower() in {"exit", "quit"}:
            print(f"{bot_name}> Bye")
            break
        print(f"{bot_name}>", respond(q, m, rows, bot_name))


if __name__ == "__main__":
    main()
