# SAPJP-pedia 実装完了レポート

## ✅ 実装完了した機能

### 1. フロントエンド (Vue.js 3 + Vuetify)
- **UIデザイン**: Grokipedia風のダークでプロフェッショナルなデザイン
- **記事閲覧**: 動的目次 (ToC) 自動生成、Markdownレンダリング（markedライブラリ）
- **記事編集**: プレビュー付きMarkdownエディタ、テンプレート入力補助
- **ファクトチェック表示**:
  - `synthesized_text`（AI検証済みテキスト）の優先表示
  - `[n]` 形式の参照番号をインタラクティブなリンクに変換
  - マウスオーバーで証拠の詳細（引用文、タイトル、ドメイン）をポップアップ表示
  - 「Verified by Grokipedia」メタデータ表示
- **管理者ダッシュボード**: 承認/却下ワークフロー
- **開発者用APIドキュメント**: 完全日本語化

### 2. バックエンド (Laravel)
- REST API (記事CRUD, 修正提案フロー, ファクトチェック結果管理)
- MySQLデータベース (`domain_ratings`, `fact_checks`, `evidences`, `evidence_chains`)
- 管理者認証 (Laravel Sanctum)

### 3. AIエージェント (Python)
- Gemini 2.0 Flash による自動ファクトチェック
- **P1完了**: エビデンスURLの実コンテンツ取得 (`fetch_page_content`)
- **P2完了**: NLI-based NLCスコアリング (`nli_scorer.py`)
  - mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 モデル
  - 文レベル分割 × 証拠チャンク比較 × 5段階判定
- **Multi-Query検索**: 記事ごとに3-5個の検索クエリを生成
- **Collect All & Score Once方式**: 全証拠を統合して一括検証

---

## 🤖 システム全体の起動手順

1. **MySQL & Apache** (XAMPP Control Panel) -> Start

2. **バックエンド**
   ```powershell
   cd c:\xampp\htdocs\sapjp-pedia\backend
   php artisan serve
   ```

3. **フロントエンド**
   ```powershell
   cd c:\xampp\htdocs\sapjp-pedia\frontend
   npm run dev
   ```

4. **AIエージェント** (必要に応じて実行)
   ```powershell
   cd c:\xampp\htdocs\sapjp-pedia\ai_agent
   pip install -r requirements.txt
   # .envにGEMINI_API_KEYを設定
   python fact_checker.py
   ```

アクセス: `http://localhost:3001`

---

## テスト結果

### P1テスト: エビデンスURL中身取得 ✅
- 単体テスト: 全7テストケース PASS
- E2Eテスト: 3記事のファクトチェック完走
- 詳細: [P1テストログ](../ai_agent/P1_TEST_LOG.md)

### P2テスト: NLIスコアリング ✅ (最適化中)

| # | 方式 | NLCスコア | 判定 |
|---|------|-----------|------|
| ① | 単一検索（英語） | 0.20 | refuted |
| ② | 〃（減点なし） | 0.44 | likely_incorrect |
| ③ | 単一検索（日本語） | **0.55** | uncertain |
| ④ | Multi-Path（パス平均） | 0.38 | likely_incorrect |
| ⑤ | Collect All（15件一括） | 0.23 | refuted |

**ベストスコア**: 方式③ (0.55) — 日本語検索 × 少数の良い証拠 × quoteあり

詳細: [P2調査ログ](../ai_agent/P2_INVESTIGATION.md)

---

## 既知の課題 (優先度順)

| 優先度 | 課題 | 状態 |
|-------|------|------|
| P1 | エビデンスURL中身取得 | ✅ 完了 |
| P2 | NLCスコア外部算出 | ✅ 完了（最適化中） |
| P3 | 認証の修復 | ❌ 未着手 |
| P4 | 自動承認の削除 | ❌ 未着手 |
| P5 | 設計書のハルシネーション除去 | ✅ 完了 |
| P6 | Docker化 | ❌ 未着手 |
| P7 | テスト追加 | ❌ 未着手 |
