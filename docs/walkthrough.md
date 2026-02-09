# SAPJP-pedia 実装完了レポート

## ✅ 実装完了した機能

### 1. フロントエンド (Vue.js)
主要画面すべて実装済み。
- **UIデザイン刷新**: Grokipedia風のダークでプロフェッショナルなデザイン (Serifフォント、余白調整)
- **データベーススキーマ修正**: 参考文献のURLやタイトルが長すぎる場合に保存エラー（500 Internal Server Error）が発生していた問題を解消するため、`references`テーブルの該当カラムを`TEXT`型に変更。
- **データクレンジング**: 信頼性の低い古い参考文献データを削除し、AIによる再生成を実施。
- **UI改善**:
  - 記事詳細画面およびプレビュー画面のMarkdownテーブルのデザインを調整し、可読性を向上（ヘッダーの折り返し防止、ボーダー・パディングの追加など）。
  - 検索バーのデザインを刷新し、`Ctrl + K`ショートカットキーのヒントをより直感的なキーボード風デザインに変更。
  - 右サイドバーの幅を縮小し、メインコンテンツの表示領域を拡大（PC表示時のバランス改善）。
  - **アクションエリアの移動**: 「編集」「履歴」などのボタンを右サイドバーから記事タイトル下のヘッダーエリアに移動・集約。により右カラムを完全に削除し、メインコンテンツ（本文）の表示幅を最大化。
  - **Grokipedia風レイアウト**: 目次エリアを左端に寄せ、メインコンテンツの最大幅制限（`max-width`）を撤廃。画面幅をフル活用した広々としたレイアウトに変更。
  - **ヘッダーの透過対応**: スクロール時に記事本文がヘッダーの背後に透けて見えないよう、`v-app-bar`に半透明の背景色（`#0F0F0F`ベース）とブラー効果（`backdrop-filter`）を追加。
  - **表示幅の最適化**: 記事エリアの最大幅を`1280px`に設定し、広すぎる画面での間延びを防止（可読性と没入感のバランス調整）。
  - **目次エリアの拡張**: 左サイドバーの幅を固定（`450px`）とし、従来の約2倍に拡張。長い見出しも折り返さずに表示可能にし、メインコンテンツとのバランスを調整。
  - **目次エリアの拡張**: 左サイドバーの幅を固定（`450px`）とし、従来の約2倍に拡張。長い見出しも折り返さずに表示可能にし、メインコンテンツとのバランスを調整。
  - **トップページ演出**: ユーザー提供のブロック文字を使用した高精細なブラックホールアスキーアートを実装。サイバーパンクかつ重厚な雰囲気を演出。


これにより、記事のファクトチェック機能が正常に動作し、信頼できる情報源に基づいたコンテンツ更新が可能になりました。
- **記事閲覧**:
  - 動的目次 (ToC) 自動生成
  - Markdownレンダリング改善 (markedライブラリ導入、テーブル表示修正)
  - 参考文献・鮮度表示
- **ブラックホール (アスキーアート):**
  - `<pre>`タグを使用したテキストベースの表現。
  - 色: `#888888` (グレー)
  - **動的エフェクト:**
    - **回転 (Spin):** 120秒周期で非常にゆっくりと回転し、降着円盤の動きを表現。
    - **呼吸 (Pulse):** 16秒周期で拡大縮小・明滅し、活動的なエネルギーを表現。
  - マスク: `radial-gradient` を使用して円形に切り抜き、四角いエッジを削除。
- **記事編集**:
  - プレビュー付きMarkdownエディタ
  - テンプレート入力補助
  - 画像アップロード（将来的な拡張を見越したUI）
- **開発者用API**:
  - ドキュメントの完全日本語化
  - カード形式のエンドポイント一覧
- **その他**:
  - 全画面の完全日本語化
  - 管理者ダッシュボード（承認フロー）

### 2. バックエンド (Laravel)
- REST API (記事CRUD, 修正提案フロー)
- MySQLデータベース
- 管理者認証 (Sanctum)

### 3. AIエージェント (Python)
- Gemini APIによる自動ファクトチェック
- 定期実行スクリプト (`fact_checker.py`)

---

## 🤖 AIエージェントの設定と実行

### 1. APIキーの設定
`ai_agent/.env` ファイルを開き、Gemini APIキーを設定してください。

```ini
GEMINI_API_KEY=your_actual_api_key_here
```

### 2. スクリプトの実行
```powershell
cd c:\xampp\htdocs\sapjp-pedia\ai_agent
python fact_checker.py
```
実行すると、登録されている記事をチェックし、必要に応じて修正提案を自動で作成します。

---

## 🚀 システム全体の起動手順

1. **MySQL & Apache** (XAMPP Control Panel) -> Start

2. **バックエンド**
   ```powershell
   cd c:\xampp\htdocs\sapjp-pedia\backend
   c:\xampp\php\php.exe artisan serve
   ```

3. **フロントエンド**
   ```powershell
   cd c:\xampp\htdocs\sapjp-pedia\frontend
   npm run dev
   ```

4. **AIエージェント** (必要に応じて実行)
   ```powershell
   cd c:\xampp\htdocs\sapjp-pedia\ai_agent
   python fact_checker.py
   ```

アクセス: `http://localhost:3001`

---

## Database Changes (2026-02-09)
Grokipediaロジックの実装に向け、以下のテーブルとモデルを追加しました。

### New Tables
*   **`domain_ratings`**: ドメインごとの信頼性スコア（PC1）を管理。
*   **`fact_checks`**: 各記事に対するファクトチェックの検証結果（統合回答、NLCスコア、伝導率など）。
*   **`evidences`**: 検証に使用された具体的な根拠（引用文、URL、スニペット）。
*   **`evidence_chains`**: 思考プロセス（ステップごとのログ）。

### Models
*   `FactCheck`, `Evidence`, `EvidenceChain`, `DomainRating`
*   `Article` モデルに `factChecks` リレーションを追加。

## Frontend Updates (Grokipedia UI)
バックエンドからのファクトチェック結果を表示するためのUI実装を行いました。

### ArticleView.vue
*   **Facts First**: 記事本文のレンダリングにおいて、`synthesized_text`（AI検証済みテキスト）が存在する場合はそれを優先表示するように変更。
*   **Interactive Evidence**: 本文中の `[n]` 形式の参照番号を検出し、インタラクティブなリンクとしてレンダリング。
*   **Evidence Popup**: 参照リンクにマウスオーバーすると、証拠の詳細（引用文、タイトル、ドメイン、Primary/Reference区分）を表示するポップアップを実装。
*   **Metadata**: 画面上部のメタデータエリアに「Verified by Grokipedia」の表示を追加（スコアバッジはユーザー要望により非表示）。

## Logic Refinement & Data Cleansing (2026-02-09)
### Issue
Previous logic truncated articles and failed to extract quotes ("No specific quote available").

### Fix
*   **Gemini API**: Increased `max_output_tokens` to ensure full article synthesis.
*   **Quote Extraction**: Implemented logic to extract specific quotes from Grounding Chunks and save them to the `evidences` table.
*   **Data Cleansing**: Sanitized the database to remove incomplete data and re-registered test articles.

### Verification Results
*   **Long Article Support**: Confirmed that long articles (e.g., "Deep Dive into SAP S/4HANA Cloud") are correctly synthesized without truncation.
*   **Quote Availability**: Confirmed that `[n]` references now display actual quoted text instead of "No specific quote available".
*   **UI Integration**: Confirmed that the frontend correctly renders these quotes in the evidence popup.
