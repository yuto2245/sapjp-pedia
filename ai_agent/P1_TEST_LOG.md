# P1 動作確認ログ

**実施日**: 2026-02-13
**対象**: `fetch_page_content` の実装検証（エビデンスURLの実コンテンツ取得）

---

## Step 1: 単体テスト (`test_p1.py`)

### 実行コマンド
```bash
cd ai_agent && python test_p1.py -v
```

### 結果: 全7テスト PASS

| # | テストケース | 種別 | 結果 |
|---|------------|------|------|
| 1 | 実在URL (Wikipedia SAP記事) からテキスト取得 | 正常系 | PASS — 3000文字取得 |
| 2 | script/style/nav/footer タグ除去 | 正常系 | PASS |
| 3 | 3000文字以内への切り詰め | 正常系 | PASS |
| 4 | 存在しないURL → 空文字列 | 異常系 | PASS — 例外で落ちない |
| 5 | タイムアウト → 空文字列 | 異常系 | PASS |
| 6 | snippet が evidence_text に含まれる | プロンプト構築 | PASS |
| 7 | verify_and_synthesize が snippet 付きでLLM呼び出し | 統合 | PASS |

### テスト中に発見・修正したバグ

**`fact_checker.py` L236-242: f-string内のJSON例文がエスケープされていない**

- 症状: `verify_and_synthesize` を呼ぶと `ValueError: Invalid format specifier` で必ずクラッシュ
- 原因: f-string内の `{ "reference_num": 1, "quote": "引用文..." }` が Python の式として解釈される
- 修正: `{` → `{{`, `}` → `}}` にエスケープ

---

## Step 2: E2Eテスト (`fact_checker.py` 実行)

### 前提条件
- バックエンド: `php artisan serve` (ポート8000)
- MySQL: XAMPP MySQL (sapjp_pedia DB)
- Gemini API: キー再発行済み

### 実行コマンド
```bash
cd ai_agent && python fact_checker.py
```

### 結果: 3記事のファクトチェックが完走

#### 記事1: SAP S/4HANA Cloud
- **Grounding chunks**: 16件発見
- **fetch_page_content 動作確認**:
  - `Fetched 3000 chars` — 複数URLで正常取得 ✅
  - `Fetched 33 chars` — 短いページも取得 ✅
  - `Fetched 0 chars → Skipping (no content fetched)` — コンテンツ取得不可のURLを正しくスキップ ✅
  - `403 Forbidden` (medium.com, researchgate.net) → 空文字列返却、スキップ ✅
- **verify_and_synthesize**: snippet付きプロンプトでLLM呼び出し ✅
- **結果**: abstained (NLC: 0.0, Cond: 0.95) — LLMレスポンスのパースに課題あり（後述）

#### 記事2: 2023へのアップグレード
- **Grounding chunks**: 9件発見
- **fetch_page_content**: 8件取得成功、1件スキップ ✅
- **結果**: abstained (NLC: 0.0, Cond: 0.9) — パース課題（後述）

#### 記事3: SAP S/4HANA Overview
- **Grounding chunks**: 10件発見
- **fetch_page_content**: 8件取得成功（33〜3000文字）、2件403でスキップ ✅
- **verify_and_synthesize**: Content付きプロンプトで呼び出し成功 ✅
- **結果**: **verified (NLC: 0.95, Cond: 0.95)** ✅
- **修正提案**: 送信・自動承認成功 ✅

### E2Eで確認できたP1修正のポイント

1. **`Fetched XXX chars from URL`** がログに出力される → `fetch_page_content` が動作している ✅
2. **`Skipping URL (no content fetched)`** が403やタイムアウトのURLに対して出る → エラーハンドリング正常 ✅
3. **LLMプロンプトに `Content:\n{snippet}` が含まれる** → `verify_and_synthesize` の evidence_text 構築正常 ✅
4. **fact_checkレコードがDBに保存される** → 3件分のレコードが作成された ✅

---

## 発見した追加課題

### 記事1・2でNLCスコアが0.0になる問題
- LLMレスポンスが期待フォーマット (`===SYNTHESIZED_TEXT===...===METADATA_JSON===...`) に従わないケースがある
- 記事1: `===METADATA_JSON===` ブロックが出力されずパース失敗 → フォールバックで0.0
- 記事2: JSONが先頭に出力され、`===SYNTHESIZED_TEXT===` が後に出る逆順パターン
- **P1スコープ外** だが、プロンプト改善で対応可能

### 403 Forbiddenになるソース
- medium.com, researchgate.net が403を返す
- User-Agentによるブロックの可能性あり
- **P1スコープ外** — コンテンツ取得不可時のスキップは正常動作

---

## 検証完了基準の達成状況

| 基準 | 達成 |
|------|------|
| 単体テスト: 全テストケースがPASS | ✅ |
| E2E: 1記事のファクトチェックが完走 | ✅ (3記事完走) |
| E2E: evidence snippetがプロンプトに含まれることをログで確認 | ✅ |
| fetch_page_content が実際にURLからコンテンツを取得 | ✅ |
| コンテンツ取得失敗時のエラーハンドリング | ✅ |

**P1検証完了** ✅
