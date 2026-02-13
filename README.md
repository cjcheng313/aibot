# POS Insight Bot MVP

MVP app for your workflow:
1. Import POS CSV files.
2. Ask the bot for daily insight in chat.
3. If you need more information, ask for a **table** or **diagram**.

Now supports:
- multi-store data (`store_id`) and store-level drill-down
- owner config (`bot_name`) shared across all owned stores
- SMS brief formatting output

## Run

```bash
python3 mvp_pos_insight_bot.py --data-dir ./data
```

With owner config:

```bash
python3 mvp_pos_insight_bot.py --data-dir ./data --config ./data/sample_account.json
```

Print SMS brief only:

```bash
python3 mvp_pos_insight_bot.py --data-dir ./data --config ./data/sample_account.json --print-sms
```

## Chat examples
- `what is my status today?`
- `show store tea-001 status`
- `stores`
- `labor`
- `waste`
- `top item`
- `table` (shows daily KPI table)
- `diagram` (shows ASCII cost-ratio chart)
- `sms` (shows SMS-ready brief text)

## CSV columns (flexible matching)
- Revenue: `revenue`, `sales`, `net_sales`, `total_sales`, `amount`
- Date: `date`, `business_date`, `transaction_date`
- Store: `store_id`, `location_id`, `store`
- Order: `order_id`, `ticket_id`, `check_id`
- Labor: `labor_cost`, `labor`, `staff_cost`
- Waste: `waste`, `waste_cost`, `spoilage`
- Item: `item`, `menu_item`, `product`

## Data architecture (recommended)
- SQL for transactions and exact metrics (orders, inventory, schedules, financials)
- Document store for flexible logs/context (chat history, notes, incidents)
- Vector DB for semantic retrieval and knowledge grounding

Rule of thumb:
- Exact numbers -> SQL
- Flexible schema/logs -> Document/NoSQL
- Text memory/semantic search -> Files + Vector DB

See:
- `docs/data_architecture.md`
- `sql/schema.sql`
- `docs/high_level_architecture.md`


## Web chat MVP

Run local web chat:

```bash
python3 web_app.py --data-dir ./data --config ./data/sample_account.json --port 8000
```

Then open: `http://localhost:8000`


## CI/CD (GitHub Actions + Render)

This repo uses a split setup:

- **GitHub Actions CI** (on PR + push to `main`):
  - compile check for `mvp_pos_insight_bot.py` and `web_app.py`
  - unit tests via `unittest`
- **Render CD**: when `Auto-Deploy` is ON, every new commit on the tracked branch triggers a redeploy automatically.

Files:
- `.github/workflows/ci-cd.yml`
- `render.yaml`

### Setup steps (auto redeploy on commit)
1. Push this repo to GitHub.
2. In Render, create a Web Service from this repo, branch `main`.
3. Ensure **Auto-Deploy = On** in Render service settings.
4. Push a commit to `main` -> Render redeploys automatically.

## Render deployment note

Recommended Render settings:
- Build command: `echo 'No build dependencies'`
- Start command: `python web_app.py --data-dir ./data --config ./data/sample_account.json --host 0.0.0.0 --port $PORT`
- Runtime: Python 3.11 (via `runtime.txt`)

If your service is still set to `pip install -r requirements.txt`, update it in the Render dashboard once and save. After that, commit-driven auto redeploy will keep working without manual steps.

- Health check URL: `/healthz` (returns service status + Render commit id when available)

### If Render logs show an old commit (example: `e7f5b2e`)
That means Render is deploying an older revision from GitHub, not your newest code.

1. Confirm your latest commit is pushed to GitHub `main`.
2. In Render service settings, ensure branch is `main` and **Auto-Deploy** is ON.
3. Click **Manual Deploy -> Deploy latest commit** once.
4. Open `/healthz` and verify `render_git_commit` matches your latest GitHub commit.

If Build Command in Render dashboard is still `pip install -r requirements.txt`, change it once to:
`echo 'No build dependencies'`
