# Grokipedia Cross-Check Algorithm v1.0

## 1. 概要
本ドキュメントは、SAPJP-pediaにおける情報の信頼性を担保するためのクロスチェックアルゴリズム「Grokipedia Logic」の設計仕様書です。
単なるWEB検索の順位付けではなく、**数理モデルに基づいた「接地 (Grounding)」の強制**と、情報の**「第一原理」的な階層化**によって、ハルシネーション（幻覚）を排除し、統計的真実を導き出すことを目的とします。

## 2. アルゴリズムの主要コンポーネント

### 2.1. No-Leap Constraint (NLC: 跳躍禁止制約)
AIが生成するすべての主張（Assertion）に対し、取得したコンテキスト内に十分な証拠が存在することを数学的に要求する制約です。

*   **判定式**: $\Gamma(a,c) \ge \tau$
    *   $a$: 主張 (Assertion)
    *   $c$: コンテキスト (Context / Evidence)
    *   $\Gamma$: スコアリング関数 (Entailment + Relevance)
    *   $\tau$: 信頼性閾値 (デフォルト: 0.95)
*   **動作**: この条件を満たさない場合、AIは回答を生成せず「Abstain (棄権)」または「要検証」ステータスを返します。

### 2.2. Domain Reliability Score (PC1: ドメイン信頼性スコア)
「専門家の知恵 (Wisdom of Experts)」に基づくアンサンブル格付けを採用し、情報のソースを定量評価します。

*   **PC1スコア**: 主成分分析 (PCA) により算出された信頼性スコア (0.00 - 1.00)。
*   **階層**:
    *   **High Quality (1.00 - 0.85)**: 公的機関、主要報道機関、公式ドキュメント (SAP Help Portal等)
    *   **Medium Quality (0.84 - 0.40)**: 専門ブログ、コミュニティフォーラム
    *   **Low Quality (0.39 - 0.00)**: 個人ブログ、掲示板、出所不明サイト

### 2.3. Semantic Physics (意味物理学)
情報の「重み」と「流れ」を物理学的指標で測定し、システムの健全性を監視します。

*   **伝導率 ($\sigma$)**: 外部エビデンスがどの程度正確に出力に反映されたかを示す指標。($\sigma \approx 0.95$ を目標)
*   **ディグニティ ($D$)**: 外部からの誘導的プロンプトやバイアスに対するシステムの自律性・耐性。

### 2.4. Statistical Truth (統計的真実)
対立する情報が存在する場合、複数の視点をその証拠の強さに応じて統合します。

1.  **概念抽出**: オープンソースデータからコア概念を抽出。
2.  **偏向測定**: 反対の立場と比較し、バイアスを測定。
3.  **バランス生成**: 「物語の確率的バランス」に基づきテキストを生成。

---

## 3. データベース設計 (Schema Update v1.1)

ユーザー要件「複数ソースに基づく回答生成」と「UIでの根拠表示（マウスオーバー・リンク）」に対応するため、スキーマを詳細化しました。

### 3.1. `domain_ratings` テーブル (新規)
ドメインごとのPC1スコアを管理するマスタテーブル。

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | BIGINT | PK |
| `domain` | VARCHAR | ドメイン名 (例: `help.sap.com`) |
| `pc1_score` | DECIMAL(5,4) | PC1スコア (0.0000 - 1.0000) |
| `category` | VARCHAR | カテゴリ (Official, News, Blog) |

### 3.2. `fact_checks` テーブル (拡張)
記事の検証結果と、**生成された統合回答**を保存します。

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | BIGINT | PK |
| `article_id` | BIGINT | FK (Articles) |
| `status` | VARCHAR | `verified`, `provisional`, `abstained` |
| `assertion_text` | TEXT | 検証対象となった主張（AI抽出） |
| `synthesized_text` | TEXT | **統合された回答文** (例: "...と言われています[1]。一方...[2]") |
| `nlc_score` | DECIMAL(5,4) | NLC判定スコア |
| `conductivity` | DECIMAL(5,4) | 伝導率 ($\sigma$) |
| `last_checked_at` | TIMESTAMP | 最終検証日時 |

### 3.3. `evidences` テーブル (新規)
回答の根拠となった具体的なソース情報。**UI表示用の引用文と参照番号**を持ちます。

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | BIGINT | PK |
| `fact_check_id` | BIGINT | FK (FactChecks) |
| `reference_num` | INT | **参照番号** (UIの `[1]`, `[2]` に対応) |
| `url` | VARCHAR | ソースURL (クリック遷移先) |
| `title` | VARCHAR | ページタイトル |
| `quote` | TEXT | **引用文** (マウスオーバーで表示) |
| `snippet` | TEXT | 検索スニペット (AI解析用) |
| `pc1_score` | DECIMAL(5,4) | その時点でのPC1スコア |
| `is_primary` | BOOLEAN | 一次情報フラグ |

### 3.4. `evidence_chain` テーブル (オプション)
思考プロセスログ（変更なし）。

---

## 4. ロジック変更詳細

### 4.1. 複数ソースに基づく「統計的真実」の生成フロー

1.  **検索 & 重み付け**:
    *   クエリに関連する上位サイトを検索し、PC1スコアで重み付けして信頼できるソース（`Primary`, `Medium`）を選定。
2.  **情報抽出 & NLC判定**:
    *   各ソースから主張に関連する箇所を抽出 (`snippet`/`quote`)。
    *   NLC ($\Gamma \ge 0.95$) をパスしたものだけを「有効なエビデンス」として採用。
3.  **統合テキスト生成**:
    *   有効なエビデンスを複数組み合わせ、AIに「統合回答 (`synthesized_text`)」を生成させる。
    *   プロンプト指示: *"対立する意見がある場合は両論併記し、文末に対応するエビデンス番号 `[n]` を付与すること。"*
4.  **データ保存**:
    *   生成されたテキストを `fact_checks.synthesized_text` に保存。
    *   使用したソース情報を `evidences` テーブルに保存し、`reference_num` でテキスト内の番号と紐付ける。

### 4.2. UI表示の仕組み
*   フロントエンドでは `synthesized_text` を解析し、`[1]`, `[2]` などの文字列を検出。
*   対応する `evidences` レコードの `quote` をツールチップで表示し、クリックで `url` へ遷移するリンクに置換する。

### 4.4. Format Refinement (Markdown整形 & 構造化)
ユーザー要望により、生成されたテキストの形式不備（不正なMarkdown、改行ミス等）を修正するプロセスを追加します。
*   **目的**: 読みやすさの担保と、フロントエンドでの表示崩れ防止。
*   **タイミング**: `synthesized_text` 生成直後（または保存後の非同期ジョブ）。
*   **処理**:
    *   専用の軽量LLMまたは正規表現を用いて、Markdownの文法チェックを行う。
    *   リストのインデント、太字/斜体の閉じ忘れ、見出しレベルの整合性などを自動修正する。
    *   DBには整形後のテキストを `synthesized_text` として保存（上書き）。

## 5. 根拠と参考資料


本アーキテクチャは、**AIの信頼性 (Trustworthy AI)** と **認識論的安全性 (Epistemic Safety)** の最新の研究成果に基づいています。

1.  **No-Leap Constraint**: AIハルシネーション抑制のための標準的なアプローチとして、RAG (Retrieval-Augmented Generation) における "Response Grounding" や "NLI-based Verification" が挙げられます。閾値 $\tau=0.95$ は高リスク領域（医療・法務）における標準的な設定です。
2.  **Wisdom of Experts (PC1)**: 複数の専門家評価をPCAで統合する手法は、メディアバイアス評価やWeb信頼性工学において有効性が示されています。
3.  **Semantic Physics**: 情報の流れを物理モデル（流体力学や熱力学）で捉える試みは、情報の伝播効率やシステムの安定性を定量化するために提案されています。

## 6. 今後のロードマップ
1.  **Phase 1**: データベース拡張とPC1スコアマスタの整備 (Current)
2.  **Phase 2**: NLC判定ロジックの実装 (`fact_checker.py` の改修)
3.  **Phase 3**: Semantic Physics メトリクスの計測と可視化
