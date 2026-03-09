import unittest

import mvp_pos_insight_bot as bot


class PosExportE2ETests(unittest.TestCase):
    def _run_export(self, csv_name: str):
        rows = bot.load_rows("data/pos_samples")
        matched = [r for r in rows if r.get("_source_file") == csv_name]
        normalized = bot.normalize(matched)
        metrics = bot.metrics(normalized)
        response = bot.respond("what is my status today?", metrics, normalized, "Miso")
        return normalized, metrics, response

    def test_square_export_works_end_to_end(self):
        normalized, metrics, response = self._run_export("square_export_sample.csv")
        self.assertGreater(len(normalized), 0)
        self.assertGreater(metrics["revenue"], 0)
        self.assertIn("Revenue", response)

    def test_toast_export_works_end_to_end(self):
        normalized, metrics, response = self._run_export("toast_export_sample.csv")
        self.assertGreater(len(normalized), 0)
        self.assertGreater(metrics["orders"], 0)
        self.assertIn("Top action", response)

    def test_clover_export_store_drilldown(self):
        normalized, metrics, _ = self._run_export("clover_export_sample.csv")
        response = bot.respond("show store la-burbank status", metrics, normalized, "Miso")
        self.assertIn("store la-burbank", response)


if __name__ == "__main__":
    unittest.main()
