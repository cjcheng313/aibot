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


## POS provider samples + end-to-end test

To simulate imports from popular POS ecosystems commonly seen in large US metro markets (including LA), this repo now includes synthetic sample exports:

- `data/pos_samples/square_export_sample.csv`
- `data/pos_samples/toast_export_sample.csv`
- `data/pos_samples/clover_export_sample.csv`

These files use different column names (for example `business_date`, `location_id`, `ticket_id`, `net_sales`) to validate the bot's flexible column matching.

### Run end-to-end tests

```bash
python3 -m unittest -v
```

### Manual test against one sample export

```bash
python3 mvp_pos_insight_bot.py --data-dir ./data/pos_samples
```

Then ask:
- `what is my status today?`
- `stores`
- `show store la-burbank status`
- `table`
- `sms`

### What data is currently included

For each row in the samples, the bot currently extracts and computes:
- date
- store id/location
- order/check/receipt id
- item/product name
- revenue/sales amount
- labor/payroll/staff cost
- waste/spoilage cost

From that, it computes daily KPIs such as revenue, order count, average order value, labor ratio, waste ratio, and top-selling item.


## Voice support (talk to the bot)

The web chat now supports browser-native voice interactions:

- **🎤 Speak**: speech-to-text for your question (Web Speech API).
- **🔊 Voice Reply**: text-to-speech for bot responses (Speech Synthesis API).

Run:

```bash
python3 web_app.py --data-dir ./data --config ./data/sample_account.json --port 8000
```

Open `http://localhost:8000`, click **🎤 Speak** to talk, and toggle **🔊 Voice Reply** to hear answers.

> Note: voice input availability depends on browser support/permissions (Chrome-family browsers usually work best).


## Owner dashboard view (trust with raw numbers)

The web app now includes a dashboard panel so owners can verify the exact metrics behind AI responses.

What the dashboard shows:
- total revenue
- total orders
- average order value
- labor ratio
- waste ratio
- top item
- per-store breakdown table (revenue, orders, avg order, labor %, waste %)

Run:

```bash
python3 web_app.py --data-dir ./data --config ./data/sample_account.json --port 8000
```

Open `http://localhost:8000` and use the **Owner Dashboard (numbers view)** panel on the right.


## Testing rule for every change

For every new feature or code change, run end-to-end validation before merge:

1. `python3 -m py_compile mvp_pos_insight_bot.py web_app.py`
2. `python3 -m unittest discover -v`

This is a required quality gate for this repo so behavior stays reliable as features grow.
