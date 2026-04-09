"""Unit tests for ``search_heading`` (no Streamlit runtime required)."""

from __future__ import annotations

import unittest

from search_heading import format_count_for_heading


class TestFormatCountForHeading(unittest.TestCase):
    def test_loading_uses_em_dash(self) -> None:
        self.assertEqual(format_count_for_heading([], loading=True), "—")
        self.assertEqual(format_count_for_heading(None, loading=True), "—")

    def test_none_logs_and_returns_zero(self) -> None:
        with self.assertLogs("search_heading", level="WARNING") as cm:
            out = format_count_for_heading(None, loading=False)
        self.assertEqual(out, "0")
        self.assertTrue(any("[SearchHeading]" in m for m in cm.output))

    def test_list_length(self) -> None:
        self.assertEqual(format_count_for_heading([], loading=False), "0")
        self.assertEqual(format_count_for_heading([{"a": 1}], loading=False), "1")
        self.assertEqual(format_count_for_heading([{}, {}, {}], loading=False), "3")


if __name__ == "__main__":
    unittest.main()
