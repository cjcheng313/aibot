import json
import threading
import time
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import web_app


class WebAppE2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        account, rows, metrics = web_app.build_state("data", "./data/sample_account.json")
        web_app.Handler.account = account
        web_app.Handler.rows = rows
        web_app.Handler.metrics = metrics

        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), web_app.Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=1)

    def _get_json(self, path: str):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}") as resp:
            self.assertEqual(resp.status, 200)
            return json.loads(resp.read().decode("utf-8"))

    def _post_json(self, path: str, payload: dict, expect_status: int = 200):
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, expect_status)
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, expect_status)
            return json.loads(exc.read().decode("utf-8"))

    def test_healthz(self):
        data = self._get_json("/healthz")
        self.assertTrue(data["ok"])

    def test_dashboard(self):
        data = self._get_json("/api/dashboard")
        self.assertIn("summary", data)
        self.assertIn("stores", data)
        self.assertGreaterEqual(len(data["stores"]), 1)

    def test_chat_success(self):
        data = self._post_json("/api/chat", {"q": "what is my status today?"})
        self.assertIn("Revenue", data["answer"])

    def test_chat_validation(self):
        data = self._post_json("/api/chat", {"q": ""}, expect_status=400)
        self.assertIn("Please ask a question.", data["answer"])


if __name__ == "__main__":
    unittest.main()
