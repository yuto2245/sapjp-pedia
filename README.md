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
- **Model**: Gemini 2.0 Flash
- **Role**: 「Grokipedia Logic」に基づく自動ファクトチェックの実行
- **Algorithm**:
  - **No-Leap Constraint (NLC)**: 証拠のない推論を排除
  - **PC1 Scoring**: ソースドメインの信頼性評価
  - **Long-text Synthesis**: 独自見解を維持しつつ、技術的誤りのみを修正

## ドキュメント

詳細な設計資料は `docs/` フォルダに格納されています。

- [Grokipedia Logic 設計仕様](docs/fact_check_design.md)
- [実装計画・変更履歴](docs/implementation_plan.md)

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
