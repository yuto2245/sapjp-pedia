# Grokipedia Cross-Check Algorithm v2.0

## 1. 概要
本ドキュメントは、SAPJP-pediaにおける情報の信頼性を担保するためのクロスチェックアルゴリズム「Grokipedia Logic」の設計仕様書です。
RAG (Retrieval-Augmented Generation) における "Response Grounding" と NLI-based Verification に基づき、ハルシネーション（幻覚）を排除し、統計的真実を導き出すことを目的とします。

## 2. アルゴリズムの主要コンポーネント

### 2.1. No-Leap Constraint (NLC: 跳躍禁止制約)
AIが生成するすべての主張（Assertion）に対し、取得したコンテキスト内に十分な証拠が存在することを要求する制約です。

*   **判定式**: $\Gamma(a,c) \ge \tau$
    *   $a$: 主張 (Assertion)
    *   $c$: コンテキスト (Context / Evidence)
    *   $\Gamma$: NLIスコアリング関数 (Entailment確率)
    *   $\tau$: 信頼性閾値（5段階分類で段階的に判定）
*   **動作**: スコアに応じて5段階（verified / likely_correct / uncertain / likely_incorrect / refuted）に分類します。

### 2.2. Domain Reliability Score (PC1: ドメイン信頼性スコア)
「専門家の知恵 (Wisdom of Experts)」に基づくアンサンブル格付けを採用し、情報のソースを定量評価します。

*   **PC1スコア**: 主成分分析 (PCA) により算出された信頼性スコア (0.00 - 1.00)。
*   **階層**:
    *   **High Quality (1.00 - 0.85)**: 公的機関、主要報道機関、公式ドキュメント (SAP Help Portal等)
    *   **Medium Quality (0.84 - 0.40)**: 専門ブログ、コミュニティフォーラム
    *   **Low Quality (0.39 - 0.00)**: 個人ブログ、掲示板、出所不明サイト

### 2.3. NLI-based Scoring (P2実装済み)
mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 モデルを使用し、合成テキストと証拠チャンクの間の entailment / neutral / contradiction を判定します。

*   **文レベル分割 (SummaC方式)**: 合成テキストを文に分割し、各文に対して最も高い entailment スコアを持つ証拠チャンクを特定
*   **矛盾検出**: contradiction > 0.7 の場合、矛盾フラグを立てる
*   **最終スコア**: 全文のweighted_scoreの平均値 × citation coverage penalty

### 2.4. 5段階判定 (多段階分類)
NLCスコアに基づき、以下の5段階で判定します（学術文献の推奨に基づく設計）。

| スコア範囲 | ステータス | 説明 |
|-----------|-----------|------|
| 0.85 - 1.00 | **verified** | 高信頼度で検証済み |
| 0.70 - 0.84 | **likely_correct** | おそらく正確 |
| 0.50 - 0.69 | **uncertain** | 不確実（人間レビュー推奨） |
| 0.30 - 0.49 | **likely_incorrect** | おそらく不正確（警告フラグ） |
| 0.00 - 0.29 | **refuted** | 高信頼度で否定 |

---

## 3. データベース設計 (Schema v1.1)

### 3.1. `domain_ratings` テーブル
ドメインごとのPC1スコアを管理するマスタテーブル。

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | BIGINT | PK |
| `domain` | VARCHAR | ドメイン名 (例: `help.sap.com`) |
| `pc1_score` | DECIMAL(5,4) | PC1スコア (0.0000 - 1.0000) |
| `category` | VARCHAR | カテゴリ (Official, News, Blog) |

### 3.2. `fact_checks` テーブル
記事の検証結果と、**生成された統合回答**を保存します。

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | BIGINT | PK |
| `article_id` | BIGINT | FK (Articles) |
| `status` | VARCHAR | `verified`, `likely_correct`, `uncertain`, `likely_incorrect`, `refuted` |
| `assertion_text` | TEXT | 検証対象となった主張（AI抽出） |
| `synthesized_text` | TEXT | **統合された回答文** (例: "...と言われています[1]。一方...[2]") |
| `nlc_score` | DECIMAL(5,4) | NLC判定スコア |
| `evidence_count` | INT | 使用した証拠の件数 |
| `last_checked_at` | TIMESTAMP | 最終検証日時 |

### 3.3. `evidences` テーブル
回答の根拠となった具体的なソース情報。**UI表示用の引用文と参照番号**を持ちます。

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | BIGINT | PK |
| `fact_check_id` | BIGINT | FK (FactChecks) |
| `reference_num` | INT | **参照番号** (UIの `[1]`, `[2]` に対応) |
| `url` | VARCHAR | ソースURL (クリック遷移先) |
| `title` | VARCHAR | ページタイトル |
| `quote` | TEXT | **引用文** (マウスオーバーで表示) |
| `snippet` | TEXT | 取得したページ内容 (NLI解析用, 最大3000文字) |
| `pc1_score` | DECIMAL(5,4) | その時点でのPC1スコア |
| `is_primary` | BOOLEAN | 一次情報フラグ |

---

## 4. ファクトチェックパイプライン

### 4.1. Collect All & Score Once 方式（現在のアーキテクチャ）

```
入力: 記事テキスト
    │
    ▼
【1. クエリ生成】Gemini APIで3-5個の検索クエリを生成
    │
    ▼
【2. Multi-Path Evidence Collection】
    │  各クエリでGemini Grounding APIを呼び出し
    │  重複URLを除外しつつ証拠を収集
    │  PC1スコア上位15件に制限
    │
    ▼
【3. ページ内容取得】
    │  各URLに対してHTTPリクエスト + BeautifulSoupでテキスト抽出
    │  script/style/nav/footer除去、最大3000文字
    │
    ▼
【4. 一括検証＆合成】
    │  全証拠をGemini APIに送り、記事の検証・再構成を行う
    │  引用文（quote）を含むMETADATA_JSONを出力
    │
    ▼
【5. NLIスコアリング】
    │  mDeBERTa NLIモデルで合成テキスト vs 証拠チャンクを比較
    │  文レベル分割 → 各文の最大entailmentスコア → 平均
    │
    ▼
【6. 結果保存】
    │  fact_checks, evidences テーブルに保存
    │  verifiedの場合のみ修正提案を送信
    │
    ▼
出力: ステータス (5段階), NLCスコア, 合成テキスト, 証拠リスト
```

### 4.2. UI表示の仕組み
*   フロントエンドでは `synthesized_text` を解析し、`[1]`, `[2]` などの文字列を検出。
*   対応する `evidences` レコードの `quote` をツールチップで表示し、クリックで `url` へ遷移するリンクに置換する。

---

## 5. 根拠と参考資料

本アーキテクチャは、**AIの信頼性 (Trustworthy AI)** と **認識論的安全性 (Epistemic Safety)** の最新の研究成果に基づいています。

1.  **No-Leap Constraint**: RAG における "Response Grounding" や "NLI-based Verification" が標準的アプローチ。
2.  **Wisdom of Experts (PC1)**: 複数の専門家評価をPCAで統合する手法は、メディアバイアス評価やWeb信頼性工学において有効性が示されている。
3.  **SummaC方式**: 文書レベルではなく文レベルでNLI比較を行うことで精度が向上（Laban et al., TACL 2022）。
4.  **多段階分類**: FEVER (3クラス)、AVeriTeC (4クラス) 等の主要データセットの設計に準拠。

詳細な学術サーベイは [nsl.md](nsl.md) を参照してください。

---

## 6. 今後のロードマップ
1.  **Phase 1**: ✅ エビデンスAPIの中身取得 (P1完了)
2.  **Phase 2**: ✅ NLI-based NLCスコアリング (P2完了)
3.  **Phase 3**: 🔄 Multi-Query Evidence Collection の最適化 (進行中)
4.  **Phase 4**: 認証修復 (P3) + 自動承認削除 (P4)
5.  **Phase 5**: Docker化 (P6) + テスト追加 (P7)
