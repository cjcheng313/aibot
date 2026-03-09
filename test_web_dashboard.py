import unittest

import mvp_pos_insight_bot as bot
import web_app


class DashboardTests(unittest.TestCase):
    def setUp(self):
        rows = bot.normalize(bot.load_rows("data"))
        metrics = bot.metrics(rows)
        self.payload = web_app.dashboard_payload(rows, metrics)

    def test_dashboard_summary_has_core_numbers(self):
        summary = self.payload["summary"]
        self.assertIn("revenue", summary)
        self.assertIn("orders", summary)
        self.assertIn("top_item", summary)

    def test_dashboard_store_rows_present(self):
        stores = self.payload["stores"]
        self.assertGreaterEqual(len(stores), 1)
        self.assertIn("store_id", stores[0])
        self.assertIn("revenue", stores[0])


if __name__ == "__main__":
    unittest.main()
