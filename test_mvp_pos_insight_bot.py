import unittest

import mvp_pos_insight_bot as bot


class BotTests(unittest.TestCase):
    def setUp(self):
        rows = bot.load_rows("data")
        self.rows = bot.normalize(rows)
        self.metrics = bot.metrics(self.rows)

    def test_summary_contains_core_fields(self):
        s = bot.summary(self.metrics)
        self.assertIn("Revenue", s)
        self.assertIn("Top action", s)

    def test_store_metrics_detected(self):
        sm = bot.store_metrics_map(self.rows)
        self.assertIn("tea-001", sm)
        self.assertIn("food-001", sm)

    def test_sms_brief(self):
        sms = bot.sms_brief(self.metrics, "Miso")
        self.assertTrue(sms.startswith("Miso:"))

    def test_store_drilldown_response(self):
        r = bot.respond("show store tea-001 status", self.metrics, self.rows, "Miso")
        self.assertIn("store tea-001", r)


if __name__ == "__main__":
    unittest.main()
