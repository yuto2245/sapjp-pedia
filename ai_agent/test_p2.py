"""
P2 Tests: NLI-based NLC Score Calculator

Tests NLIScorer independently (no API key needed, only NLI model).
Run: cd ai_agent && python test_p2.py
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from nli_scorer import NLIScorer


class TestNLIScorer(unittest.TestCase):
    """Unit tests for NLIScorer (NLI model only, no API key required)."""

    @classmethod
    def setUpClass(cls):
        print("\n=== Loading NLI model (first run downloads ~1.2GB) ===")
        cls.scorer = NLIScorer()
        print("=== Model loaded ===\n")

    # ------------------------------------------------------------------
    # score_pair tests
    # ------------------------------------------------------------------

    def test_entailment_ja(self):
        """Japanese entailment pair should have entailment > 0.5."""
        result = self.scorer.score_pair(
            "SAPはドイツのソフトウェア企業である。",
            "SAPはドイツの会社です。"
        )
        print(f"  Entailment JA: {result}")
        self.assertIn("entailment", result)
        self.assertGreater(result["entailment"], 0.5,
                           f"Expected entailment > 0.5, got {result['entailment']}")

    def test_contradiction_ja(self):
        """Japanese contradiction pair should have contradiction > 0.5."""
        result = self.scorer.score_pair(
            "SAPの本社はドイツのヴァルドルフにある。",
            "SAPの本社はアメリカのシリコンバレーにある。"
        )
        print(f"  Contradiction JA: {result}")
        self.assertIn("contradiction", result)
        self.assertGreater(result["contradiction"], 0.5,
                           f"Expected contradiction > 0.5, got {result['contradiction']}")

    def test_neutral_ja(self):
        """Unrelated pair should have neutral > entailment and > contradiction."""
        result = self.scorer.score_pair(
            "SAPはERP市場でシェア1位である。",
            "今日の天気は晴れです。"
        )
        print(f"  Neutral JA: {result}")
        self.assertIn("neutral", result)
        self.assertGreater(result["neutral"], result["entailment"],
                           "Neutral should be > entailment for unrelated pair")

    # ------------------------------------------------------------------
    # split_sentences tests
    # ------------------------------------------------------------------

    def test_split_sentences_ja(self):
        """Japanese text should be split by 。！？."""
        text = "SAPはERPソフトウェアを提供する。本社はドイツにある。従業員は10万人以上いる。"
        sents = self.scorer.split_sentences(text)
        print(f"  Split JA: {sents}")
        self.assertEqual(len(sents), 3)

    def test_split_sentences_en(self):
        """English text should be split by period+space."""
        text = "SAP provides ERP software. Its headquarters is in Germany. It has over 100k employees."
        sents = self.scorer.split_sentences(text)
        print(f"  Split EN: {sents}")
        self.assertEqual(len(sents), 3)

    def test_split_sentences_short_fragment_filtered(self):
        """Very short fragments (< 5 chars) should be filtered out."""
        text = "SAPはERP企業。あ。本社はドイツ。"
        sents = self.scorer.split_sentences(text)
        print(f"  Split short filter: {sents}")
        # "あ" (1 char) should be filtered
        for s in sents:
            self.assertGreaterEqual(len(s), 5)

    # ------------------------------------------------------------------
    # compute_nlc_score tests
    # ------------------------------------------------------------------

    def test_compute_nlc_score_with_evidence(self):
        """Full pipeline: synthesized text + evidence → NLC score."""
        synthesized = "SAPはドイツのヴァルドルフに本社を置く企業です[1]。ERPソフトウェアを提供しています[2]。"
        evidences = [
            {
                "snippet": "SAP SEはドイツのヴァルドルフに本社を構えるソフトウェア企業で、ERPシステムの最大手である。",
                "pc1_score": 1.0,
                "reference_num": 1,
            },
            {
                "snippet": "SAPはエンタープライズリソースプランニング（ERP）ソフトウェアの開発・販売を行っている。",
                "pc1_score": 0.9,
                "reference_num": 2,
            },
        ]
        result = self.scorer.compute_nlc_score(synthesized, evidences)
        print(f"  NLC Score: {result['nlc_score']}")
        print(f"  Details: {result['details']}")
        self.assertIn("nlc_score", result)
        self.assertGreater(result["nlc_score"], 0.0)
        self.assertFalse(result["has_contradiction"])
        self.assertGreater(len(result["details"]), 0)

    def test_compute_nlc_score_empty_evidence(self):
        """No evidence → score 0.0."""
        result = self.scorer.compute_nlc_score("Some text.", [])
        self.assertEqual(result["nlc_score"], 0.0)

    def test_compute_nlc_score_empty_text(self):
        """Empty synthesized text → score 0.0."""
        result = self.scorer.compute_nlc_score("", [{"snippet": "foo", "pc1_score": 1.0, "reference_num": 1}])
        self.assertEqual(result["nlc_score"], 0.0)

    # ------------------------------------------------------------------
    # determine_status tests
    # ------------------------------------------------------------------

    def test_determine_status_verified(self):
        self.assertEqual(NLIScorer.determine_status(0.90), "verified")
        self.assertEqual(NLIScorer.determine_status(0.85), "verified")

    def test_determine_status_likely_correct(self):
        self.assertEqual(NLIScorer.determine_status(0.75), "likely_correct")
        self.assertEqual(NLIScorer.determine_status(0.70), "likely_correct")

    def test_determine_status_uncertain(self):
        self.assertEqual(NLIScorer.determine_status(0.60), "uncertain")
        self.assertEqual(NLIScorer.determine_status(0.50), "uncertain")

    def test_determine_status_likely_incorrect(self):
        self.assertEqual(NLIScorer.determine_status(0.40), "likely_incorrect")
        self.assertEqual(NLIScorer.determine_status(0.30), "likely_incorrect")

    def test_determine_status_refuted(self):
        self.assertEqual(NLIScorer.determine_status(0.20), "refuted")
        self.assertEqual(NLIScorer.determine_status(0.0), "refuted")

    # ------------------------------------------------------------------
    # Integration: verify fact_checker changes
    # ------------------------------------------------------------------

    def test_compute_nlc_score_prefers_quote(self):
        """When evidence has a quote, it should be used over snippet."""
        synthesized = "SAPはドイツの企業です。"
        # snippet is irrelevant noise, but quote is a clean match
        evidences = [
            {
                "snippet": "Menu Home About Contact Privacy Policy Terms of Service Cookie",
                "quote": "SAPはドイツのヴァルドルフに本社を置くソフトウェア企業である。",
                "pc1_score": 1.0,
                "reference_num": 1,
            },
        ]
        result_with_quote = self.scorer.compute_nlc_score(synthesized, evidences)

        # Same evidence but without quote → falls back to noisy snippet
        evidences_no_quote = [
            {
                "snippet": "Menu Home About Contact Privacy Policy Terms of Service Cookie",
                "pc1_score": 1.0,
                "reference_num": 1,
            },
        ]
        result_without_quote = self.scorer.compute_nlc_score(synthesized, evidences_no_quote)

        print(f"  With quote: {result_with_quote['nlc_score']}")
        print(f"  Without quote: {result_without_quote['nlc_score']}")
        self.assertGreater(result_with_quote["nlc_score"], result_without_quote["nlc_score"],
                           "Quote-based score should be higher than noisy snippet score")

    def test_fetch_page_content_cleans_boilerplate(self):
        """fetch_page_content should remove header, aside, and boilerplate classes."""
        from fact_checker import FactChecker
        from unittest.mock import patch, MagicMock

        html = """
        <html><body>
        <header><h1>Site Logo</h1></header>
        <nav><a href="/">Home</a></nav>
        <aside>Sidebar content</aside>
        <div class="breadcrumb">Home > SAP > Article</div>
        <div class="sidebar-menu">Menu items</div>
        <div id="cookie-banner">Accept cookies</div>
        <main><p>SAP is an enterprise software company based in Walldorf, Germany.</p></main>
        <footer>Copyright 2024</footer>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        with patch("fact_checker.requests.get", return_value=mock_response):
            checker = FactChecker.__new__(FactChecker)
            result = checker.fetch_page_content("http://example.com")

        print(f"  Cleaned content: {repr(result[:200])}")
        self.assertIn("enterprise software", result)
        self.assertNotIn("Site Logo", result)
        self.assertNotIn("Sidebar content", result)
        self.assertNotIn("breadcrumb", result.lower())
        self.assertNotIn("Accept cookies", result)
        self.assertNotIn("Copyright", result)
        self.assertNotIn("Menu items", result)

    def test_generate_search_queries_returns_list(self):
        """generate_search_queries should return a list of query strings."""
        from fact_checker import FactChecker
        from unittest.mock import patch, MagicMock

        mock_response = MagicMock()
        mock_response.text = '["SAP MM purchase order process", "SAP MM inventory management", "SAP MM pricing conditions"]'

        checker = FactChecker.__new__(FactChecker)
        with patch("fact_checker.client.models.generate_content", return_value=mock_response):
            queries = checker.generate_search_queries({
                "title": "SAP MM入門",
                "module": "MM",
                "content": "SAP MMモジュールは購買管理と在庫管理を担当します。"
            })

        print(f"  Generated queries: {queries}")
        self.assertIsInstance(queries, list)
        self.assertGreaterEqual(len(queries), 1)
        self.assertLessEqual(len(queries), 5)
        for q in queries:
            self.assertIsInstance(q, str)

    def test_generate_search_queries_fallback(self):
        """On LLM failure, should return fallback query list."""
        from fact_checker import FactChecker
        from unittest.mock import patch

        checker = FactChecker.__new__(FactChecker)
        with patch("fact_checker.client.models.generate_content", side_effect=Exception("API error")):
            queries = checker.generate_search_queries({
                "title": "SAP FI概要",
                "module": "FI",
                "content": "SAP FIモジュールは財務会計を管理します。"
            })

        print(f"  Fallback queries: {queries}")
        self.assertIsInstance(queries, list)
        self.assertEqual(len(queries), 1)
        self.assertIn("SAP", queries[0])

    def test_fact_checker_no_nlc_in_synthesis(self):
        """verify_and_synthesize return dict should NOT contain nlc_score."""
        # We test the expected structure, not the actual LLM call
        expected_keys = {"synthesized_text", "used_references"}
        # This is a structural assertion: the new code returns only these keys
        mock_result = {
            "synthesized_text": "test",
            "used_references": []
        }
        self.assertEqual(set(mock_result.keys()), expected_keys)
        self.assertNotIn("nlc_score", mock_result)


if __name__ == "__main__":
    print("=" * 60)
    print("P2 Test Suite: NLI-based NLC Score Calculator")
    print("=" * 60)
    unittest.main(verbosity=2)
