import os
import time
import requests
import json
import re
import numpy as np
from datetime import datetime
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from dotenv import load_dotenv
import schedule
from bs4 import BeautifulSoup
from nli_scorer import NLIScorer

# 環境変数の読み込み
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api")

if not API_KEY:
    print("Error: GEMINI_API_KEY is not set in .env")
    exit(1)

client = genai.Client(api_key=API_KEY)

class FactChecker:
    def __init__(self):
        self.nli_scorer = NLIScorer()
        self.domains = {
            "help.sap.com": 1.0,
            "sap.com": 1.0,
            "support.sap.com": 1.0,
            "learning.sap.com": 1.0,
            "news.sap.com": 0.9,
            "reuters.com": 0.9,
            "bloomberg.com": 0.9,
            "techcrunch.com": 0.8,
            "wikipedia.org": 0.7,
            "stackoverflow.com": 0.6,
            "qiita.com": 0.5,
            "zenn.dev": 0.5,
            "note.com": 0.4
        }

    def get_pc1_score(self, url):
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        # サブドメインを含む完全一致、または部分一致で検索
        for key, score in self.domains.items():
            if key in domain:
                return score
        return 0.5  # Default

    def check_articles(self):
        print("\n=== Starting Grokipedia Logic Fact Check Cycle ===")
        try:
            response = requests.get(f"{BACKEND_URL}/search")
            if response.status_code != 200:
                print(f"Failed to fetch articles: {response.status_code}")
                return

            articles = response.json()
            print(f"Found {len(articles)} articles.")

            for article_summary in articles:
                self.process_article(article_summary['id'])

        except Exception as e:
            print(f"Error during check cycle: {e}")

    # ------------------------------------------------------------------
    # Multi-Path Verification: 複数クエリで証拠を広く集め、最後に一括スコアリング
    # ------------------------------------------------------------------
    def process_article(self, article_id):
        try:
            # 1. 記事詳細取得
            res = requests.get(f"{BACKEND_URL}/articles/{article_id}")
            if res.status_code != 200:
                print(f"Failed to get article {article_id}")
                return
            article = res.json()
            print(f"Processing: {article['title']}")

            # 2. FactCheckレコード作成 (Pending)
            fc_res = requests.post(f"{BACKEND_URL}/fact-checks", json={
                "article_id": article_id,
                "status": "pending",
                "assertion_text": article['title'] + "\n" + article['content'][:200]
            })
            if fc_res.status_code != 201:
                print(f"Failed to create fact_check record: {fc_res.text}")
                return
            fact_check_id = fc_res.json()['id']

            # 3. Multi-Path Evidence Collection
            queries = self.generate_search_queries(article)
            print(f"\n  === Multi-Path Evidence Collection: {len(queries)} queries ===")

            all_evidences = []
            seen_urls = set()

            for path_idx, query in enumerate(queries):
                print(f"\n  --- Query {path_idx + 1}/{len(queries)}: {query} ---")

                # 個別クエリで検索
                path_evidences = self._search_single_query(query)
                for ev in path_evidences:
                    if ev['url'] not in seen_urls:
                        seen_urls.add(ev['url'])
                        ev['reference_num'] = len(all_evidences) + 1
                        all_evidences.append(ev)

                print(f"  -> Query {path_idx + 1}: {len(path_evidences)} results, Total: {len(all_evidences)} unique")

            # PC1スコアの高い順にソートし、上位15件に制限
            all_evidences.sort(key=lambda e: e['pc1_score'], reverse=True)
            all_evidences = all_evidences[:15]
            for i, ev in enumerate(all_evidences):
                ev['reference_num'] = i + 1

            print(f"\n  === Evidence Collection Complete: {len(all_evidences)} evidences ===")

            # 4. 一括検証＆合成（全証拠を使用）
            synthesis_result = self.verify_and_synthesize(article, all_evidences)

            # EvidenceにQuoteをマージ
            used_refs = synthesis_result.get('used_references', [])
            print(f"  -> used_references count: {len(used_refs)}")
            for ref in used_refs:
                ref_num = ref.get('reference_num')
                quote = ref.get('quote') or ''
                try:
                    print(f"  -> Ref#{ref_num} quote: {quote[:80]}..." if len(quote) > 80 else f"  -> Ref#{ref_num} quote: {quote}")
                except UnicodeEncodeError:
                    print(f"  -> Ref#{ref_num} quote: (encoding error, {len(quote)} chars)")
                for ev in all_evidences:
                    if ev['reference_num'] == ref_num:
                        ev['quote'] = quote
                        break

            # 5. NLI-based NLC Score（一括スコアリング）
            nlc_result = self.nli_scorer.compute_nlc_score(
                synthesis_result['synthesized_text'], all_evidences
            )
            nlc_score = nlc_result['nlc_score']
            status = self.nli_scorer.determine_status(nlc_score)

            # 6. DBにEvidence保存
            if all_evidences:
                requests.post(f"{BACKEND_URL}/fact-checks/{fact_check_id}/evidences", json={
                    "evidences": all_evidences
                })

            # 7. Update FactCheck Record
            requests.put(f"{BACKEND_URL}/fact-checks/{fact_check_id}", json={
                "status": status,
                "synthesized_text": synthesis_result['synthesized_text'],
                "nlc_score": nlc_score,
                "evidence_count": len(all_evidences),
                "last_checked_at": datetime.now().isoformat()
            })

            print(f"  -> Result: {status} (NLI Score: {nlc_score}, Contradiction: {nlc_result['has_contradiction']})")

            # 8. 修正提案 (verifiedの場合のみ)
            if status == "verified":
                 self.submit_proposal(article, synthesis_result, all_evidences, nlc_score)

        except Exception as e:
            print(f"Error checking article {article_id}: {e}")

    def fetch_page_content(self, url):
        """URLからページ内容を取得し、テキストを抽出する"""
        try:
            response = requests.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (compatible; SAPJPpedia-FactChecker/1.0)"
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'form', 'noscript']):
                tag.decompose()
            # Remove common boilerplate by class/id patterns
            for tag in soup.find_all(attrs={"class": re.compile(r'(menu|sidebar|breadcrumb|cookie|banner|ad-|social|share)', re.I)}):
                tag.decompose()
            for tag in soup.find_all(attrs={"id": re.compile(r'(menu|sidebar|breadcrumb|cookie|banner|footer|header)', re.I)}):
                tag.decompose()
            text = soup.get_text(separator='\n', strip=True)
            text = text[:3000]
            print(f"  -> Fetched {len(text)} chars from {url}")
            return text
        except Exception as e:
            print(f"  -> Failed to fetch {url}: {e}")
            return ""

    def generate_search_queries(self, article):
        """LLMに記事を読ませて検証用の検索クエリを3-5個生成させる"""
        prompt = f"""以下のSAP技術記事を検証するための検索クエリを生成してください。
記事の各セクションの事実主張をカバーするように、3〜5個の英語検索クエリを生成してください。

ルール:
- 各クエリは記事の異なるセクション/トピックを対象にすること
- "SAP"を含めること
- 公式ドキュメントや技術リファレンスが見つかるようなクエリにすること
- JSON配列のみを返すこと: ["query1", "query2", ...]

【記事タイトル】{article['title']}
【モジュール】{article['module']}
【記事内容】
{article['content'][:3000]}"""

        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=GenerateContentConfig(max_output_tokens=1024)
            )
            text = response.text.strip()
            # JSON配列を抽出（コードブロックで囲まれている場合も対応）
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                queries = json.loads(json_match.group())
                # 3-5個に制限
                queries = [q for q in queries if isinstance(q, str)][:5]
                if queries:
                    return queries
        except Exception as e:
            print(f"  -> Query generation failed: {e}")

        # フォールバック: 従来の固定クエリ
        return [f"SAP {article['module']} {article['title']} official documentation"]

    # def search_and_collect_evidence(self, article):
    #     """Multi-Path Verification導入により不要。process_article内で直接処理。"""
    #     print("  -> Searching Google...")
    #     queries = self.generate_search_queries(article)
    #     print(f"  -> Generated {len(queries)} search queries")
    #
    #     all_evidences = []
    #     seen_urls = set()
    #
    #     for query in queries:
    #         print(f"  -> Searching: {query}")
    #         new_evidences = self._search_single_query(query)
    #         for ev in new_evidences:
    #             if ev['url'] not in seen_urls:
    #                 seen_urls.add(ev['url'])
    #                 ev['reference_num'] = len(all_evidences) + 1
    #                 all_evidences.append(ev)
    #
    #     # PC1スコアの高い順にソートし、上位15件に制限（合成プロンプトの肥大化を防ぐ）
    #     all_evidences.sort(key=lambda e: e['pc1_score'], reverse=True)
    #     all_evidences = all_evidences[:15]
    #     # reference_numを振り直し
    #     for i, ev in enumerate(all_evidences):
    #         ev['reference_num'] = i + 1
    #     print(f"  -> Total unique evidences: {len(all_evidences)}")
    #     return all_evidences

    def _search_single_query(self, query):
        """単一クエリでGemini Grounding APIを呼び出し、evidenceリストを返す"""
        tools = [Tool(google_search=GoogleSearch())]
        config = GenerateContentConfig(tools=tools)

        prompt = f"Find official SAP documentation and reliable technical articles about: {query}"

        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=config
            )

            evidences = []
            if hasattr(response, "candidates") and response.candidates:
                meta = response.candidates[0].grounding_metadata
                if meta and meta.grounding_chunks:
                    print(f"  -> Found {len(meta.grounding_chunks)} grounding chunks.")
                    for i, chunk in enumerate(meta.grounding_chunks):
                        if chunk.web:
                            url = chunk.web.uri
                            title = chunk.web.title
                            snippet = self.fetch_page_content(url)
                            if not snippet:
                                print(f"  -> Skipping {url} (no content fetched)")
                                continue
                            pc1 = self.get_pc1_score(url)

                            evidences.append({
                                "url": url,
                                "title": title,
                                "snippet": snippet,
                                "quote": "",
                                "reference_num": len(evidences) + 1,
                                "pc1_score": pc1,
                                "is_primary": pc1 >= 0.9
                            })
            return evidences
        except Exception as e:
            print(f"  -> Search failed: {e}")
            return []

    def verify_and_synthesize(self, article, evidences):
        print("  -> Verifying and Synthesizing...")
        
        evidence_text = ""
        for ev in evidences:
            snippet = ev.get('snippet', '')
            evidence_text += f"[{ev['reference_num']}] Title: {ev['title']}\nURL: {ev['url']}\nPC1: {ev['pc1_score']}\nContent:\n{snippet}\n\n"

        prompt = f"""
        あなたは厳格なSAPファクトチェッカーです。
        以下の【記事】の内容を、与えられた【証拠リスト】のみを用いて検証し、
        Grokipediaの「No-Leap Constraint (NLC)」に従って再構成してください。

        【重要指示】
        1. あなたの役割は、記事の内容を「No-Leap Constraint」に基づいて検証・補強することです。
        2. 各証拠にはソースページから取得した実際のテキスト内容（Content）が含まれています。**検証は必ずこのContentに書かれている情報のみに基づいて行ってください。あなた自身の訓練データや事前知識を根拠にしてはいけません。**
        3. 【証拠リスト】のContentに基づいて裏付けが取れた箇所には、必ず `[1]` のような出典番号を付与してください。quoteにはContentから該当する記述を正確に引用してください。
        4. 【情報の完全性】証拠リストのContentに該当する情報がない場合でも、元の【記事】の記述は削除せず、そのまま維持してください。**記事の全てのセクション、全ての段落を網羅し、絶対に途中で切ったり省略したりしないでください。**
        5. ただし、証拠リストのContentと明らかに矛盾する内容（明らかな事実誤認）が見つかった場合は、証拠に基づいて修正してください。
        6. 可能な限り、複数の証拠のContentに基づいた多角的な検証を心がけてください。
        7. **出力形式**: 以下の形式で出力してください。JSON全体ではなく、特定の部分のみJSONにします。

        ===SYNTHESIZED_TEXT===
        (ここに再構成された記事全文をMarkdown形式で出力。途中で切れないように全て出力すること)
        ===END_SYNTHESIZED_TEXT===

        ===METADATA_JSON===
        {{
            "used_references": [
                {{ "reference_num": 1, "quote": "引用文..." }},
                {{ "reference_num": 2, "quote": "..." }}
            ]
        }}
        ===END_METADATA_JSON===

        【記事】
        {article['content'][:5000]}...

        【証拠リスト】
        {evidence_text}
        """

        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=GenerateContentConfig(
                    max_output_tokens=8192
                )
            )
            
            text = response.text
            print(f"DEBUG: AI Response length: {len(text)} chars")
            print(f"DEBUG: Contains METADATA_JSON: {'===METADATA_JSON===' in text}")
            print(f"DEBUG: Contains END_METADATA_JSON: {'===END_METADATA_JSON===' in text}")

            
            # Parse SYNTHESIZED_TEXT
            syn_match = re.search(r'===SYNTHESIZED_TEXT===(.*?)===END_SYNTHESIZED_TEXT===', text, re.DOTALL)
            synthesized_text = syn_match.group(1).strip() if syn_match else article['content']
            
            # Parse METADATA_JSON
            meta_match = re.search(r'===METADATA_JSON===(.*?)===END_METADATA_JSON===', text, re.DOTALL)
            metadata = json.loads(meta_match.group(1).strip()) if meta_match else {"used_references": []}

            return {
                "synthesized_text": synthesized_text,
                "used_references": metadata.get('used_references', [])
            }

        except Exception as e:
            print(f"  -> Synthesis failed: {e}")
            # Fallback
            return {"synthesized_text": article['content'], "used_references": []}

    def submit_proposal(self, article, synthesis_result, evidences, nlc_score=0.0):
        print("  -> Submitting Proposal...")

        # Reference URL list
        urls = [ev['url'] for ev in evidences if ev['pc1_score'] >= 0.8]

        payload = {
            "creator_type": "ai",
            "reason": f"[Grokipedia Verified] NLI-based NLC Score: {nlc_score}",
            "after_content": synthesis_result['synthesized_text'],
            "reference_urls": urls
        }
        
        try:
            res = requests.post(f"{BACKEND_URL}/articles/{article['id']}/propose", json=payload)
            if res.status_code == 201:
                report_id = res.json().get('report_id')
                # 自動承認
                requests.patch(f"{BACKEND_URL}/reports/{report_id}/approve")
                print("  -> Correction applied successfully.")
        except Exception as e:
            print(f"  -> Proposal submission failed: {e}")

if __name__ == "__main__":
    checker = FactChecker()
    checker.check_articles()
