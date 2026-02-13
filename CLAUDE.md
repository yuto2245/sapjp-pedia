# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

SAPJP-pediaは、SAPの知識を共有・蓄積するナレッジプラットフォーム。AIによる自動ファクトチェック機能を備える。3つのサービスで構成:

- **Backend** (`/backend`): Laravel 12 (PHP 8.2+) — 記事CRUD、API提供、ファクトチェック結果保存、MySQL、Sanctum認証
- **Frontend** (`/frontend`): Vue 3 + Vite + Vuetify + Pinia — 記事の閲覧・編集、ファクトチェック結果表示
- **AI Agent** (`/ai_agent`): Python — Gemini 2.0 Flashベースのファクトチェックエンジン（単一ファイル: `fact_checker.py`）

## 開発コマンド

### Backend (Laravel)
```bash
cd backend
composer install
cp .env.example .env && php artisan key:generate
php artisan migrate
composer dev          # サーバー(8000)、キューワーカー、ログ、Viteを同時起動
composer test         # PHPUnitテスト実行（config:clear後）
php artisan serve     # サーバーのみ起動（ポート8000）
php artisan test --filter=TestName  # 単一テスト実行
./vendor/bin/pint     # コードフォーマット（Laravel Pint）
```

### Frontend (独立したVueアプリ)
```bash
cd frontend
npm install
npm run dev           # 開発サーバー（ポート3001）
npm run build         # プロダクションビルド
```

### AI Agent (Python)
```bash
cd ai_agent
pip install -r requirements.txt
# .envにGEMINI_API_KEYを設定
python fact_checker.py
```

## アーキテクチャ

### サービス間通信
- Laravel ↔ Frontend: REST API (`/api/*`)
- Laravel → Python AI: HTTP内部通信（Python側 `POST /verify`, `GET /health`）
- 責務分離の原則: **「LLMが必要か？ Yes → Python、No → Laravel」**

### 主要APIルート (`backend/routes/api.php`)
- `GET /api/search` — 記事の全文検索
- `GET|POST /api/articles` — 記事CRUD
- `POST /api/articles/{id}/propose` — 修正提案の送信
- `GET /api/reports/pending`, `PATCH /api/reports/{id}/approve|reject` — 提案の管理
- `POST /api/fact-checks` — AIエージェントによるファクトチェック結果の登録
- 注意: 管理者ルートの一部が「開発用」として認証なしで公開中

### フロントエンドルート (`frontend/src/router/index.js`)
- `/` — ホーム、`/articles/:id` — 記事詳細、`/editor` — 記事作成
- `/articles/:id/history` — 修正履歴、`/articles/:id/propose` — 修正提案
- `/admin` — 管理ダッシュボード、`/developer/api` — 開発者APIドキュメント

### ファクトチェックパイプライン（コアロジック: `ai_agent/fact_checker.py`）
1. 記事テキストからクレーム（検証可能な事実主張）を抽出し、主観的意見と分離
2. 第1段階スクリーニング: LLMが「明らかに正しい / 要検証 / 意見」にトリアージ
3. 第2段階: 要検証クレームのみ外部ソース（Brave Search、Wikipedia）で本格検証
4. クロスリファレンスマトリクス: 2ソース照合 → Verified / Likely Correct / Disputed 等
5. 修正提案をLaravel APIに送信、人間による承認が必須（Human-in-the-Loop）

## 既知の課題 (`CLAUDE_HANDOFF.md`より)

`CLAUDE_HANDOFF.md`に詳細記載。優先順:
- **P1**: エビデンスURLのページ内容を実際に取得していない — LLMが訓練データだけで「検証したフリ」をしている
- **P2**: NLCスコアをLLM自身に自己評価させている（外部算出すべき）
- **P3**: 管理者ルートの認証が開発用として無効化されている
- **P4**: AIが自分の修正提案を自動承認している（人間の承認を待つべき）
- **P5**: 設計書にLLMのハルシネーションが混入（「Semantic Physics」等）
- **P6**: Docker化されていない
- **P7**: テストがない

## 設計原則

1. **Human-in-the-Loop**: AIの修正提案は必ず人間が承認する
2. **段階的フィルタリング**: 全クレームを同じ深さで検証しない、コスト最適化
3. **ソースの独立性**: 照合先のソース同士が互いに依存していないこと
4. **透明性**: 検証ロジックがブラックボックスにならない、根拠を必ず示す
5. **プラグイン設計**: ソースプロバイダーとLLMプロバイダーは差し替え可能にする
