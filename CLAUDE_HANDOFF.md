# SAPJP-pedia Claude Code 引き継ぎドキュメント

## このファイルについて
このドキュメントは、SAPJP-pediaプロジェクトの設計議論・コードレビュー・改善方針をまとめた引き継ぎ資料です。
Claude Codeでの開発作業時に、このファイルをコンテキストとして読み込んでください。

---

## 1. プロジェクト概要

### ビジョン
ユーザーがアップロードしたナレッジファイル（Markdown記事）を定期的にファクトチェックし、検証・補完するオープンソースプログラム。Grokipediaに着想を得ている。

### 現在の状態
- リポジトリ: https://github.com/yuto2245/sapjp-pedia/tree/develop
- 3サービス構成（Laravel + Vue.js + Python AIエージェント）が動作する状態
- ファクトチェックの基本フローは実装済みだが、コアロジックに重大な欠陥がある

---

## 2. アーキテクチャ

### 確定した技術スタック

```
【Laravel側（メインバックエンド）】
- フレームワーク:    Laravel 11+
- フロントエンド:    Vue.js 3 + Vuetify
- DB:              MySQL
- 認証:            Laravel Sanctum
- 役割: ユーザー認証、記事CRUD、ファクトチェック結果の保存・返却、API公開

【Python側（AIマイクロサービス）】
- フレームワーク:    FastAPI（現在は素のスクリプト → 要リファクタリング）
- LLM:             Gemini 2.0 Flash（現在）→ LiteLLMで抽象化して複数LLM対応予定
- 検索ソース:       Brave Search API + Wikipedia API（将来Grokipedia等も追加可能に）
- 役割: ファクトチェックのコアロジックのみ

【責務の分離原則】
「LLMを呼ぶ必要があるか？」がYes → Python、No → Laravel
```

### サービス間通信
- Laravel → Python: HTTP（内部通信）
- 非同期キュー方式を推奨（LaravelのQueue機能でジョブ管理）
- Python側エンドポイント: `POST /verify`（ドキュメント検証）、`GET /health`

---

## 3. 最重要の改善事項（優先順で）

### 【P1】エビデンスの中身を取得していない（致命的） — 修正済み・未検証

**現状の問題:**
`search_and_collect_evidence`メソッドがGemini APIの`grounding_chunks`からURLとタイトルだけを取得し、ページの実際の内容を取得していない。`verify_and_synthesize`にはURLとタイトルのみが渡され、LLMは自身の訓練データの知識で「検証したフリ」をしている。

**修正内容（実装済み・未検証）:**
1. `fetch_page_content`メソッドを新規追加 — URLにHTTPリクエストを送り、BeautifulSoupでテキスト抽出（script/style/nav/footer除去、最大3000文字）
2. `search_and_collect_evidence`で各grounding chunkのURLに対して`fetch_page_content`を呼び出し、取得テキストを`snippet`キーとして追加。内容が取れなかったURLはスキップ
3. `verify_and_synthesize`の証拠リスト構築部分で、タイトル・URLに加えて`snippet`（実際のページ内容）をプロンプトに含めるよう修正

**修正箇所:** `ai_agent/fact_checker.py` — `fetch_page_content`（新規）、`search_and_collect_evidence`、`verify_and_synthesize`

### 【P2】NLCスコアをLLM自身に自己評価させている

**現状の問題:**
プロンプトで「nlc_scoreを出力せよ」と指示し、LLMが自分で0.95等の数値を返している。自分の回答を自分で採点しており、客観的検証になっていない。

**修正方針:**
NLCスコアはLLMの外部で算出する。具体的には:
- クレーム内のキーファクトがソーステキストに含まれているかのキーワードマッチ率
- 複数ソース間の一致度
- ソースの信頼度（PC1スコア）の加重平均
これらを組み合わせた独自スコアリング関数を実装する。

### 【P3】認証が無効化されている

**現状の問題:**
`api.php`で記事作成・提案承認・却下が「開発用」として認証なしで公開されている。

**修正方針:**
- AIエージェント用のAPIキー認証を最低限追加
- `auth:sanctum`のコメントアウトを解除し、管理者ルートを保護

### 【P4】AIが自分の修正提案を自動承認している

**現状の問題:**
`submit_proposal`メソッドの最後で`requests.patch(f"{BACKEND_URL}/reports/{report_id}/approve")`を呼んでおり、AIが提案→AIが承認という状態。

**修正方針:**
自動承認を削除。提案は必ず「pending」状態でDBに保存し、管理ダッシュボードから人間が承認/却下する。

### 【P5】設計書にLLMのハルシネーションが混入している

**現状の問題:**
`docs/fact_check_design.md`に記載されている「Semantic Physics（意味物理学）」「伝導率σ」「ディグニティD」等の概念は、設計時にLLMが生成したハルシネーション（もっともらしいが実在しない概念）であり、学術的根拠がない。実装上も`measure_conductivity`は参照番号の正規表現マッチとエビデンス数による簡易計算であり、「物理モデル」とは無関係。これらの用語がドキュメントに残っていると、プロジェクトの信頼性を損なう。

**修正方針:**
1. `docs/fact_check_design.md`からSemantic Physics、伝導率σ、ディグニティD関連のセクション（2.3節）を削除
2. `fact_checks`テーブルの`conductivity`カラムを削除または用途を再定義
3. `fact_checker.py`の`measure_conductivity`メソッドを削除し、P2の外部スコアリングに統合
4. 設計書全体を見直し、実装されている機能（NLC判定、PC1スコア、統合テキスト生成）のみを正確に記述する
5. 根拠セクション（5節）の「Semantic Physics」の参考資料記述も削除

### 【P6】Docker化

**現状の問題:**
XAMPPベースの起動手順。他の開発者が環境を再現できない。

**修正方針:**
docker-compose.ymlを作成し、以下のサービスを定義:
- `laravel-app` (PHP + Nginx)
- `python-ai` (FastAPI + Uvicorn)
- `mysql`
- `redis` (キュー用)
- `queue-worker` (Laravel Queue Worker)

### 【P7】テストがない

**修正方針:**
最低限、以下のテストを追加:
- Python: クレーム抽出の入出力テスト、スコアリング関数のテスト
- Laravel: APIエンドポイントのFeatureテスト

---

## 4. ファクトチェック コアロジックの設計

### 長文ドキュメントのコスト最適化: 段階的フィルタリング

全クレームを同じ深さで検証するとコストが爆発する。安いチェックで大半を振り分け、疑わしいものだけ本格検証する。

```
入力ドキュメント (例: クレーム100個)
    │
    ▼
【第1段階：LLMによる一括スクリーニング】 ← LLM呼び出し少数回
    │  チャンク単位でまとめてLLMに渡し、
    │  「明らかに正しい / 要検証 / 意見」に振り分ける
    │
    ├── 明らかに正しい (70個) → LLMの知識で十分 → 低コスト判定
    ├── 意見・主観 (15個)     → 検証対象外としてスキップ
    └── 要検証 (15個)         → 第2段階へ
           │
           ▼
  【第2段階：外部ソースで本格検証】 ← API呼び出し 15回のみ
           │
           ▼
       検証結果
```

### クレーム（Claim）の定義
「クレーム」＝文中の「事実として検証可能な主張」。センテンスそのものではない。
- 「2011年にTaylor Otwellによって作られた」→ クレーム（検証可能）
- 「開発体験が素晴らしい」→ 意見（検証対象外）
LLMに抽出させる際、「検証可能な事実主張」と「主観的意見」を分離させる。

### 照合判定マトリクス（2ソース参照時）

| ソースA結果 | ソースB結果 | 判定 | 信頼度 |
|---|---|---|---|
| 支持 | 支持 | **Verified** | 高 (0.85-1.0) |
| 支持 | 該当なし | **Likely Correct** | 中 (0.5-0.7) |
| 該当なし | 支持 | **Likely Correct** | 中 (0.5-0.7) |
| 該当なし | 該当なし | **Unverified** | 低 |
| 支持 | 矛盾 | **Disputed** | — |
| 矛盾 | 矛盾 | **Likely Incorrect** | 高 |

### ソースプロバイダーの設計（プラグイン方式）

```
ソースプロバイダー (共通インターフェース)
    │
    ├── BraveSearchProvider   (Web検索) ← 初期実装
    ├── WikipediaProvider     (構造化知識) ← 初期実装
    ├── GrokipediaProvider    (リアルタイムAI知識) ← 将来追加
    ├── ScholarProvider       (学術論文) ← 将来追加
    └── CustomProvider        (ユーザー指定ソース) ← 将来追加
```

各プロバイダーは「クエリを受け取り、ソース情報（テキスト内容を含む）のリストを返す」という同一インターフェースを満たす。

### LLM抽象化

現在はGemini 2.0 Flashに直接依存している。LiteLLMを導入し、外部API（OpenAI/Anthropic/Gemini）とローカルLLM（Ollama等）の両方に対応できるようにする。初期は外部APIで動作させ、インターフェースだけ抽象化しておく。

---

## 5. 収益化戦略（参考）

コードに直接関係しないが、設計判断に影響する情報として記載。

### 主要収益モデル
1. **マネージドSaaS**: ホスティング版を月額課金。無料枠（50件/月1回チェック）→ 有料枠
2. **API課金**: 他ツール（Notion、Confluence等）との連携API、従量課金
3. **コンサルティング**: 企業への導入支援

### OSSとしての設計含意
- コアロジックはOSSとして公開（信頼性の担保）
- SaaS版では運用の手間を省く付加価値で課金
- ソースプロバイダーのプラグイン方式はマーケットプレイス化の布石

---

## 6. 既存コードの構成（参照用）

```
sapjp-pedia/
├── README.md
├── fix_schema.sql          ← 削除してマイグレーションに統合すべき
├── docs/
│   ├── fact_check_design.md   ← 設計書（実装との乖離あり、要更新）
│   ├── implementation_plan.md ← 実装計画
│   └── walkthrough.md         ← 実装完了レポート
├── backend/                   ← Laravel 11
│   ├── app/
│   │   ├── Http/Controllers/Api/
│   │   │   ├── ArticleController.php
│   │   │   ├── FactCheckController.php
│   │   │   └── ReportController.php
│   │   └── Models/
│   │       ├── Article.php
│   │       ├── FactCheck.php
│   │       ├── Evidence.php
│   │       ├── DomainRating.php
│   │       └── ...
│   ├── database/migrations/
│   └── routes/api.php         ← 認証が一部無効化されている
├── frontend/                  ← Vue.js 3 + Vuetify
│   └── src/
│       ├── views/
│       │   ├── HomeView.vue
│       │   ├── ArticleView.vue
│       │   ├── EditorView.vue
│       │   └── ...
│       └── api.js
└── ai_agent/                  ← Python（要リファクタリング）
    ├── fact_checker.py        ← コアロジック（全処理が1ファイルに集中）
    └── requirements.txt
```

---

## 7. 推奨する作業順序

```
Phase 1: コアロジック修正（最優先）
  1. エビデンスのURL先の中身を実際に取得する処理を追加
  2. NLCスコアを外部スコアリングに変更
  3. fact_checker.pyをモジュール分割（抽出/検索/照合/集約）
  4. 自動承認を削除

Phase 2: インフラ整備
  5. Docker化（docker-compose.yml作成）
  6. 認証の修正（API認証の復活）
  7. fix_schema.sqlをマイグレーションに統合

Phase 3: 拡張
  8. LiteLLMによるLLM抽象化
  9. ソースプロバイダーのプラグイン化
  10. テスト追加
  11. 設計書の更新（実装と一致させる）
```

---

## 8. 設計原則（コード全体に適用）

1. **責務の分離**: LLMが必要 → Python、それ以外 → Laravel
2. **Human-in-the-Loop**: AIの修正提案は必ず人間が承認する
3. **段階的フィルタリング**: 全クレームを同じ深さで検証しない、コスト最適化
4. **ソースの独立性**: 照合先のソース同士が互いに依存していないことを確認
5. **透明性**: 検証ロジックがブラックボックスにならない、根拠を必ず示す
6. **抽象化**: LLMプロバイダーとソースプロバイダーは差し替え可能に設計する
