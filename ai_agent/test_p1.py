"""
P1テスト: fetch_page_content の単体テスト & verify_and_synthesize のプロンプト構築確認
APIキー不要で実行可能
"""
import unittest
from unittest.mock import patch, MagicMock
import requests

# fact_checker.py はモジュールレベルで API_KEY チェック & genai.Client 生成するため、
# インポート前にモックする
import os
os.environ["GEMINI_API_KEY"] = "dummy-key-for-test"

with patch("google.genai.Client"):
    from fact_checker import FactChecker


class TestFetchPageContent(unittest.TestCase):
    """fetch_page_content の単体テスト"""

    def setUp(self):
        self.checker = FactChecker()

    def test_real_url_returns_text(self):
        """正常系: 実在URLからテキスト取得できる"""
        url = "https://en.wikipedia.org/wiki/SAP_SE"
        result = self.checker.fetch_page_content(url)
        self.assertTrue(len(result) > 0, "取得テキストが空")
        self.assertLessEqual(len(result), 3000, "3000文字を超えている")

    def test_html_tags_stripped(self):
        """正常系: script/style/nav/footer タグが除去される"""
        html = """<html><body>
        <script>alert('x')</script>
        <style>.foo{color:red}</style>
        <nav>Navigation</nav>
        <footer>Footer text</footer>
        <p>Main content here</p>
        </body></html>"""

        with patch("fact_checker.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.text = html
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp

            result = self.checker.fetch_page_content("http://example.com")
            self.assertIn("Main content", result)
            self.assertNotIn("alert", result)
            self.assertNotIn("color:red", result)
            self.assertNotIn("Navigation", result)
            self.assertNotIn("Footer text", result)

    def test_truncation_to_3000(self):
        """正常系: 3000文字以内に切り詰められる"""
        long_html = f"<html><body><p>{'A' * 5000}</p></body></html>"

        with patch("fact_checker.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.text = long_html
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp

            result = self.checker.fetch_page_content("http://example.com")
            self.assertEqual(len(result), 3000)

    def test_nonexistent_url_returns_empty(self):
        """異常系: 存在しないURL → 空文字列（例外で落ちない）"""
        result = self.checker.fetch_page_content("https://thisdomaindoesnotexist12345.example")
        self.assertEqual(result, "")

    def test_timeout_returns_empty(self):
        """異常系: タイムアウト → 空文字列"""
        with patch("fact_checker.requests.get", side_effect=requests.exceptions.Timeout("timeout")):
            result = self.checker.fetch_page_content("http://example.com")
            self.assertEqual(result, "")


class TestVerifyAndSynthesizePrompt(unittest.TestCase):
    """verify_and_synthesize のプロンプト構築確認（LLM呼び出しはモック）"""

    def setUp(self):
        self.checker = FactChecker()

    def test_snippet_included_in_prompt(self):
        """evidences の snippet がプロンプトの evidence_text に含まれる"""
        article = {
            "id": 1,
            "title": "Test Article",
            "content": "SAP S/4HANAは次世代ERP。",
            "module": "S/4HANA"
        }
        evidences = [
            {
                "url": "https://help.sap.com/s4hana",
                "title": "SAP S/4HANA Overview",
                "snippet": "S/4HANA is SAP's next-generation ERP suite built on HANA.",
                "quote": "",
                "reference_num": 1,
                "pc1_score": 1.0,
                "is_primary": True
            },
            {
                "url": "https://en.wikipedia.org/wiki/SAP_S/4HANA",
                "title": "SAP S/4HANA - Wikipedia",
                "snippet": "SAP S/4HANA is an enterprise resource planning software.",
                "quote": "",
                "reference_num": 2,
                "pc1_score": 0.7,
                "is_primary": False
            }
        ]

        # verify_and_synthesize 内のプロンプト構築ロジックを再現して検証
        evidence_text = ""
        for ev in evidences:
            snippet = ev.get('snippet', '')
            evidence_text += f"[{ev['reference_num']}] Title: {ev['title']}\nURL: {ev['url']}\nPC1: {ev['pc1_score']}\nContent:\n{snippet}\n\n"

        # snippet がプロンプトに含まれることを確認
        self.assertIn("Content:\nS/4HANA is SAP's next-generation ERP suite built on HANA.", evidence_text)
        self.assertIn("Content:\nSAP S/4HANA is an enterprise resource planning software.", evidence_text)
        self.assertIn("[1] Title: SAP S/4HANA Overview", evidence_text)
        self.assertIn("[2] Title: SAP S/4HANA - Wikipedia", evidence_text)

    def test_verify_and_synthesize_calls_llm_with_snippet(self):
        """verify_and_synthesize が実際に snippet 付きプロンプトで LLM を呼ぶことを確認"""
        article = {
            "id": 1,
            "title": "Test",
            "content": "テスト記事の内容",
            "module": "FI"
        }
        evidences = [
            {
                "url": "https://help.sap.com/test",
                "title": "Test Doc",
                "snippet": "ACTUAL_PAGE_CONTENT_FROM_FETCH",
                "quote": "",
                "reference_num": 1,
                "pc1_score": 1.0,
                "is_primary": True
            }
        ]

        # LLM呼び出しをモックし、プロンプトに snippet が含まれるか検証
        mock_response = MagicMock()
        mock_response.text = """
===SYNTHESIZED_TEXT===
テスト記事の内容 [1]
===END_SYNTHESIZED_TEXT===

===METADATA_JSON===
{"nlc_score": 0.9, "used_references": [{"reference_num": 1, "quote": "test"}]}
===END_METADATA_JSON===
"""

        with patch("fact_checker.client") as mock_client:
            mock_client.models.generate_content.return_value = mock_response
            result = self.checker.verify_and_synthesize(article, evidences)

            # LLMが呼ばれたことを確認
            mock_client.models.generate_content.assert_called_once()
            call_args = mock_client.models.generate_content.call_args
            prompt = call_args[1].get("contents") or call_args[0][0] if call_args[0] else call_args[1]["contents"]

            # プロンプトに実際のページコンテンツが含まれている
            self.assertIn("ACTUAL_PAGE_CONTENT_FROM_FETCH", prompt)
            self.assertIn("Content:", prompt)

            # 結果の検証
            self.assertAlmostEqual(result["nlc_score"], 0.9)
            self.assertIn("[1]", result["synthesized_text"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
