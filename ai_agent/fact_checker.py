import os
import time
import requests
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from dotenv import load_dotenv
import schedule
import json
import re

# 環境変数の読み込み
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api")

# Gemini API設定
if not API_KEY:
    print("Error: GEMINI_API_KEY is not set in .env")
    exit(1)

client = genai.Client(api_key=API_KEY)

def check_articles():
    print("Starting fact check cycle...")
    try:
        # 全記事取得
        response = requests.get(f"{BACKEND_URL}/search")
        if response.status_code != 200:
            print(f"Failed to fetch articles: {response.status_code}")
            return

        articles = response.json()
        print(f"Found {len(articles)} articles.")

        for article_summary in articles:
            article_id = article_summary['id']
            # 詳細取得
            detail_res = requests.get(f"{BACKEND_URL}/articles/{article_id}")
            if detail_res.status_code != 200:
                continue
            
            article = detail_res.json()
            process_article(article)

    except Exception as e:
        print(f"Error during check cycle: {e}")

def process_article(article):
    print(f"Checking article: {article['title']}")
    
    # プロンプト作成
    prompt = f"""
    あなたはSAPの専門家です。Google検索ツールを使用して、以下の記事の内容を事実確認（ファクトチェック）してください。
    必ず実際に検索を行い、最新のSAP公式ドキュメントや信頼できる技術情報を探してください。

    記事タイトル: {article['title']}
    モジュール: {article['module']}
    
    現在の記事内容:
    {article['content']}

    ---
    検証結果に基づき、以下の点を判定してください：
    1.  内容に誤りや古い情報、重要な欠落がある場合は `needs_revision: true` としてください。
    2.  `reference_urls` には、**今回の検索で実際に見つけた**信頼できる情報源のURLを含めてください（架空のURLは禁止）。
    3.  `after_content` には修正後の記事全文を記述してください。

    回答は以下のJSON形式のみで出力してください。Markdownのコードブロックは不要です。
    {{
        "needs_revision": true/false,
        "reason": "修正が必要な理由（検索で見つけた情報に基づき具体的に）",
        "after_content": "修正後の記事全文（Markdown形式）",
        "reference_urls": ["https://help.sap.com/...", ...]
    }}
    """

    try:
        # Google Search Grounding を有効化
        tools = [Tool(google_search=GoogleSearch())]
        config = GenerateContentConfig(
            tools=tools
        )

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=config
        )
        
        # レスポンス解析
        # 以前のSDKと同様に text 属性があるか確認、なければ parts から取得
        text = ""
        if hasattr(response, "text") and response.text:
            text = response.text
        elif hasattr(response, "candidates") and response.candidates:
             if response.candidates[0].content and response.candidates[0].content.parts:
                 text = response.candidates[0].content.parts[0].text

        # JSONパース（念のためMarkdown除去と制御文字削除）
        text = re.sub(r'^```(json)?\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
        
        # 制御文字の除去（改行・タブ以外）
        text = "".join(ch for ch in text if ch == '\n' or ch == '\t' or ch >= ' ')
        
        text = text.strip()

        try:
            result = json.loads(text)
        except json.JSONDecodeError as je:
            print(f"  -> JSON Decode Error: {je}")
            # エラー時はデバッグ用に一部を出力
            print(f"  -> Raw Text (start): {text[:100]}...")
            return

        if result.get("needs_revision"):
            print(f"  -> Revision needed: {result['reason']}")
            # Grounding Metadataの確認（デバッグ用）
            if hasattr(response, "candidates") and response.candidates:
                meta = response.candidates[0].grounding_metadata
                if meta and meta.grounding_chunks:
                     print(f"  -> Grounding Chunks found: {len(meta.grounding_chunks)}")

            submit_proposal(article['id'], result)
        else:
            print("  -> No revision needed.")

    except Exception as e:
        print(f"  -> Error checking article: {e}")

def submit_proposal(article_id, result):
    payload = {
        "creator_type": "ai",
        "reason": f"[AI Fact Check] {result['reason']}",
        "after_content": result['after_content'],
        "reference_urls": result.get("reference_urls", [])
    }
    
    try:
        # 1. 提案を作成
        res = requests.post(f"{BACKEND_URL}/articles/{article_id}/propose", json=payload)
        
        if res.status_code == 201:
            data = res.json()
            report_id = data.get('report_id')
            print(f"  -> Proposal submitted (ID: {report_id}).")
            
            # 2. 即座に承認（記事更新）
            if report_id:
                approve_res = requests.patch(f"{BACKEND_URL}/reports/{report_id}/approve")
                if approve_res.status_code == 200:
                    print("  -> Proposal APPROVED and Article UPDATED successfully.")
                else:
                    print(f"  -> Failed to approve proposal: {approve_res.status_code}")
        else:
            print(f"  -> Failed to submit proposal: {res.status_code} {res.text}")

    except Exception as e:
        print(f"  -> Error submitting/approving proposal: {e}")

if __name__ == "__main__":
    # 即時実行
    check_articles()

