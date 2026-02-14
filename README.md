# SAPJP-pedia

SAPの知識を共有・蓄積するためのナレッジプラットフォーム。AIによる自動ファクトチェック機能を備え、情報の信頼性を担保します。

## プロジェクト構成

### 1. Backend (`/backend`)
- **Framework**: Laravel (PHP)
- **Role**: 記事管理、API提供、ファクトチェック結果の保存
- **Main APIs**:
  - `/api/articles`: 記事のCRUD
  - `/api/fact-checks`: ファクトチェック履歴の管理
  - `/api/search`: 全文検索・AIエージェント向け検索

### 2. Frontend (`/frontend`)
- **Framework**: Vue 3 + Vite
- **UI Library**: Vuetify
- **Role**: 記事の閲覧、編集、ファクトチェック結果（引用・ソースリンク）の表示

### 3. AI Agent (`/ai_agent`)
- **Language**: Python
- **Model**: Gemini 2.0 Flash + mDeBERTa NLI
- **Role**: 「Grokipedia Logic」に基づく自動ファクトチェックの実行
- **ファイル構成**:
  - `fact_checker.py`: コアロジック（検索・合成・検証）
  - `nli_scorer.py`: NLIスコアリング（mDeBERTa）
- **Algorithm**:
  - **Multi-Query Search**: 記事から複数クエリ生成→Gemini Grounding APIで証拠収集
  - **No-Leap Constraint (NLC)**: 証拠のない推論を排除
  - **NLI-based Scoring**: mDeBERTaモデルによる外部スコアリング（5段階判定）
  - **PC1 Scoring**: ソースドメインの信頼性評価

## ドキュメント

| ファイル | 内容 |
|---------|------|
| [fact_check_design.md](docs/fact_check_design.md) | Grokipedia Logic 設計仕様 |
| [implementation_plan.md](docs/implementation_plan.md) | システム設計書 |
| [walkthrough.md](docs/walkthrough.md) | 実装完了レポート |
| [nsl.md](docs/nsl.md) | 学術的先行研究サーベイ |

## セットアップ

### Backend
1. `cd backend`
2. `composer install`
3. `cp .env.example .env` (DB設定等を行う)
4. `php artisan migrate`
5. `php artisan serve` (port 8000)

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev` (port 3001)

### AI Agent
1. `cd ai_agent`
2. `pip install -r requirements.txt`
3. `.env` に `GEMINI_API_KEY` を設定
4. `python fact_checker.py` で実行

