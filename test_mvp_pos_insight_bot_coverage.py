import json
import tempfile
import unittest
from pathlib import Path

import mvp_pos_insight_bot as bot
import web_app


class BotFunctionCoverageTests(unittest.TestCase):
    def setUp(self):
        self.rows = bot.normalize(bot.load_rows("data"))
        self.metrics = bot.metrics(self.rows)

    def test_match_col_exact_and_fuzzy(self):
        cols = ["Business_Date", "Net Sales", "Store Location"]
        self.assertEqual(bot._match_col(cols, ["business_date"]), "Business_Date")
        self.assertEqual(bot._match_col(cols, ["location"]), "Store Location")
        self.assertIsNone(bot._match_col(cols, ["unknown_col"]))

    def test_to_float_parsing(self):
        self.assertEqual(bot._to_float("1,234.50"), 1234.5)
        self.assertEqual(bot._to_float("bad-number"), 0.0)

    def test_load_account_config_defaults(self):
        cfg = bot.load_account_config(None)
        self.assertEqual(cfg["owner_name"], "Owner")
        self.assertEqual(cfg["bot_name"], bot.DEFAULT_BOT_NAME)

    def test_load_account_config_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "account.json"
            p.write_text(json.dumps({"owner_name": "A", "bot_name": "B", "stores": ["s1"]}))
            cfg = bot.load_account_config(str(p))
            self.assertEqual(cfg["owner_name"], "A")
            self.assertEqual(cfg["bot_name"], "B")
            self.assertEqual(cfg["stores"], ["s1"])

    def test_load_rows_raises_when_no_csv(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(FileNotFoundError):
                bot.load_rows(td)

    def test_normalize_empty(self):
        self.assertEqual(bot.normalize([]), [])

    def test_metrics_empty_rows(self):
        m = bot.metrics([])
        self.assertEqual(m["revenue"], 0)
        self.assertEqual(m["orders"], 0)

    def test_store_metrics_map_and_top_action(self):
        sm = bot.store_metrics_map(self.rows)
        self.assertTrue(sm)
        action = bot.top_action(self.metrics)
        self.assertIsInstance(action, str)
        self.assertGreater(len(action), 0)

    def test_summary_and_sms(self):
        s = bot.summary(self.metrics)
        sms = bot.sms_brief(self.metrics, "Miso")
        self.assertIn("Revenue", s)
        self.assertTrue(sms.startswith("Miso:"))

    def test_daily_table_and_diagram(self):
        table = bot.daily_table(self.rows)
        chart = bot.diagram(self.metrics)
        self.assertIn("date", table)
        self.assertIn("Labor", chart)

    def test_parse_store_request(self):
        store = bot._parse_store_request("show store tea-001 status", ["tea-001", "food-001"])
        self.assertEqual(store, "tea-001")
        store = bot._parse_store_request("show store food-001", ["tea-001", "food-001"])
        self.assertEqual(store, "food-001")

    def test_respond_branches(self):
        self.assertIn("Known stores", bot.respond("stores", self.metrics, self.rows, "Miso"))
        self.assertIn("Labor cost", bot.respond("labor", self.metrics, self.rows, "Miso"))
        self.assertIn("Waste cost", bot.respond("waste", self.metrics, self.rows, "Miso"))
        self.assertIn("Top item", bot.respond("top item", self.metrics, self.rows, "Miso"))
        self.assertIn("Miso:", bot.respond("sms", self.metrics, self.rows, "Miso"))
        self.assertIn("Ask me:", bot.respond("unrecognized", self.metrics, self.rows, "Miso"))

    def test_web_build_state(self):
        account, rows, metrics = web_app.build_state("data", "./data/sample_account.json")
        self.assertIn("bot_name", account)
        self.assertGreater(len(rows), 0)
        self.assertIn("revenue", metrics)


if __name__ == "__main__":
    unittest.main()
