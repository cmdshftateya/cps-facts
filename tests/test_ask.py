"""The private chart bot's data side: read-only SQL, chart checks, outlier labels. No API calls."""
import unittest
from types import SimpleNamespace as NS

from tools.ask import server

SCATTER = """SELECT s.school_id, s.name,
  MAX(CASE WHEN v.metric='pct_low_income' AND v.school_year='2024-25' THEN v.value END) AS x,
  MAX(CASE WHEN v.metric='math_growth' AND v.school_year='2024-25' THEN v.value END) AS y
FROM schools s JOIN vals v USING (school_id) GROUP BY s.school_id HAVING x IS NOT NULL AND y IS NOT NULL"""


class TestAsk(unittest.TestCase):
    def test_writes_rejected(self):
        for sql in ("DELETE FROM vals", "DROP TABLE schools", "WITH a AS (SELECT 1) DELETE FROM vals"):
            with self.assertRaises(Exception):
                server.run_query(sql, 10)
        self.assertGreater(server.run_query("SELECT COUNT(*) FROM vals", 1)[1][0][0], 60000)

    def test_suppressed_is_null_not_zero(self):
        _, rows, _ = server.run_query("SELECT COUNT(*) FROM vals WHERE status='suppressed' AND value IS NOT NULL", 1)
        self.assertEqual(rows[0][0], 0)

    def test_scatter_labels_outliers(self):
        chart, summary = server.build_chart({"kind": "scatter", "sql": SCATTER, "title": "t", "y_label": "y",
                                             "label_outliers": 5, "label_names": ["DEWEY"]})
        self.assertGreater(summary["points"], 400)
        labeled = [p["name"] for p in chart["points"] if p.get("outlier")]
        self.assertIn("DEWEY", labeled)
        self.assertEqual(len(summary["labeled_outliers"]), len(labeled))
        self.assertLessEqual(len(labeled), 6)

    def test_missing_columns(self):
        with self.assertRaises(ValueError):
            server.build_chart({"kind": "scatter", "sql": "SELECT name, 1 AS y FROM schools", "title": "t", "y_label": "y"})

    def test_dictionary_marks_breaks(self):
        self.assertIn("`iar_math_prof`", server.SYSTEM)
        self.assertIn("BREAK at 2024-25", server.SYSTEM)

    def test_builder_is_deterministic_and_checked(self):
        req = {"kind": "scatter", "x": {"metric": "pct_low_income", "year": "2024-25"},
               "y": {"metric": "math_growth", "year": "2024-25"}, "filters": {"band": ["ES"]}, "label_outliers": 5}
        a, sa = server.plot(req)
        b, _ = server.plot(req)
        self.assertEqual([p["name"] for p in a["points"] if p.get("outlier")],
                         [p["name"] for p in b["points"] if p.get("outlier")])
        self.assertIn("2024-25", a["subtitle"])
        self.assertIn("never counted as zero", a["note"])
        bad = [{**req, "x": {"metric": "nope", "year": "2024-25"}},
               {**req, "y": {"metric": "math_growth", "year": "2026-27"}},
               {**req, "filters": {"band": ["ES') OR 1=1 --"]}}]
        self.assertRaises(ValueError, server.plot, bad[0])
        self.assertRaises(ValueError, server.plot, bad[1])
        self.assertEqual(server.plot(bad[2])[1]["points"], 482)   # unknown filter value ignored, not injected
        bar, _ = server.plot({"kind": "bar", "y": {"metric": "ppe_total", "year": "2024-25"}, "top": 5})
        self.assertEqual(len(bar["points"]), 5)
        self.assertEqual(server.build_chart({**bar})[1]["points"], 5)   # its SQL re-runs as shown

    def test_conversation_loop_with_fake_model(self):
        usage = NS(input_tokens=100, output_tokens=50, cache_read_input_tokens=0, cache_creation_input_tokens=0)
        turns = iter([
            NS(stop_reason="tool_use", usage=usage, content=[
                NS(type="tool_use", id="t1", name="make_chart",
                   input={"kind": "scatter", "sql": SCATTER, "title": "t", "y_label": "y"}),
                NS(type="tool_use", id="t2", name="run_sql", input={"sql": "DELETE FROM vals"})]),
            NS(stop_reason="end_turn", usage=usage, content=[NS(type="text", text="Davis M leads.")]),
        ])
        sent = []
        fake = NS(beta=NS(messages=NS(create=lambda **kw: (sent.append(kw), next(turns))[1])))
        orig, server.client = server.client, lambda: fake
        try:
            out = server.ask("test", "math growth vs poverty")
        finally:
            server.client = orig
            server.CONVERSATIONS.pop("test", None)
        self.assertEqual(out["text"], "Davis M leads.")
        self.assertEqual(len(out["charts"]), 1)
        results = sent[1]["messages"][-2]["content"]  # history list is shared; the final reply follows
        self.assertFalse(results[0].get("is_error"))
        self.assertTrue(results[1]["is_error"])          # the write was refused, and the model is told
        self.assertEqual(sent[0]["model"], server.MODEL)


if __name__ == "__main__":
    unittest.main()
