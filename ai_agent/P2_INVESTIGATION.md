# P2 調査結果: NLCスコアの外部算出

**調査日**: 2026-02-13

---

## 1. 現状の問題

### nlc_score の使用箇所

| 場所 | ファイル | 使われ方 |
|------|---------|---------|
| AI Agent | `fact_checker.py:237` | LLMプロンプトで自己採点させる |
| AI Agent | `fact_checker.py:122-125` | ステータス判定 (`≥0.8` → verified, `≥0.5` → provisional) |
| Backend | `FactCheck.php:20` | fillable/cast定義 |
| Backend | `ArticleController.php:66` | 記事詳細APIに返却 |
| Backend | マイグレーション:30 | `decimal(5,4)` カラム |
| Frontend | — | 直接表示は未実装 |

### measure_conductivity の分析結果

- 参照番号の正規表現マッチ (`+0.3`) + エビデンス数 × `0.05`
- エビデンス6件以上で常に0.8超え → **ゲートとして機能していない**
- **結論: 削除可能**（P5と連動）。「参照番号チェック」のみNLCのCoverage軸に統合

### 設計書 vs 実装の不整合

| 項目 | 設計書 | 実装 |
|------|-------|------|
| NLC閾値 | τ=0.95 | 0.8 |
| conductivity | 物理モデル（σ） | 正規表現+エビデンス数 |
| ステータス分類 | 未定義 | 3段階 (verified/provisional/abstained) |

---

## 2. NLIモデルの選択肢比較

### 日本語対応NLIモデル

| モデル | パラメータ | 日本語精度 | メモリ | CPU速度(15ペア) | 矛盾検出 |
|--------|-----------|----------|--------|----------------|---------|
| **mDeBERTa-v3-base-xnli-2mil7** | 300M | XNLI ~80-83% | ~1.2GB | ~3秒 | 可能 |
| luke-japanese-base-finetuned-jnli | 300M | JNLI 89.77% | ~1.2GB | ~3秒 | 可能 |
| multilingual-e5-small (Embedding) | 100M | MRR@10 89.1 | ~400MB | ~0.5秒 | **不可** |

### 学術的先行研究との対応 (nsl.md調査より)

| 手法 | モデルサイズ | 性能 | 日本語 | 適用性 |
|------|-----------|------|--------|--------|
| MiniCheck-FT5 | 770M | GPT-4同等、AlignScore+4.3% | 英語中心 | 要ファインチューン |
| AlignScore | 355M | TRUE/SummaC SOTA | 英語中心 | 要ファインチューン |
| HHEM 2.1 | ~180M | AUC 0.872 | 英語中心 | 軽量だが英語 |
| SummaC-Conv | RoBERTa-large | BA 74.4% | 英語中心 | 文分割手法は採用可能 |

### 推奨モデル

**第一推奨: `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`**

理由:
1. 日本語を含む27言語で明示的にfine-tune済み
2. 3クラス分類（entailment/neutral/contradiction）で矛盾検出可能
3. CPU環境で15ペア約3秒 — 実用的
4. メモリ約1.2GB — Windows環境で問題なし
5. 決定的出力 — 再現性あり
6. 無料 — API依存なし

**補助: `intfloat/multilingual-e5-small`** — NLI入力長制限(512トークン)超のエビデンス事前フィルタリング用

---

## 3. スコアリング設計案

### 学術的知見の統合

nsl.md調査から得られた3つの核心的知見:

1. **文レベル分割が必須** (SummaC): NLIモデルに文書全体を入力すると性能が大幅低下
2. **τ=0.95は高すぎる**: 学術文献の最も厳格な例でも0.9が上限。多段階分類を推奨
3. **パイプライン型が構造的に優れる**: 単純乗算(ドメイン×NLC)よりクレーム単位検証

### 提案するスコアリングパイプライン

```
合成テキスト (synthesized_text)
    │
    ▼
【文レベル分割】 (SummaC方式)
    │  合成テキストを文単位に分割
    │
    ▼
【各文 × 各エビデンスのNLIスコア行列】
    │  mDeBERTa-v3-base-xnli で3クラス確率算出
    │  → entailment / neutral / contradiction
    │
    ▼
【Coverage計算】
    │  合成テキスト中の引用 [n] が実際のエビデンスに対応するか
    │  → quote がエビデンスsnippetに含まれるかチェック
    │
    ▼
【スコア集約】
    │  - 各文の最大entailmentスコア（最良エビデンスとの対応）
    │  - PC1スコア（ソース信頼度）による重み付け
    │  - contradiction検出時のペナルティ
    │  → 文スコアの平均 = NLCスコア
    │
    ▼
【多段階分類】 (5段階)
    ≥0.85  → "verified"       (高信頼度で検証済み)
    0.70-  → "likely_correct"  (おそらく正確)
    0.50-  → "uncertain"       (人間レビュー必要)
    0.30-  → "likely_incorrect" (おそらく不正確)
    <0.30  → "refuted"         (高信頼度で否定)
```

### 閾値の扱い

- 初期値は上記5段階を使用
- 将来的にはラベル付きデータを蓄積し、ROC曲線+Youden's J統計量で最適化
- Temperature Scalingによるキャリブレーションも検討

---

## 4. 実装に必要な変更

### 新規追加
- `ai_agent/nli_scorer.py` — NLIスコアリングモジュール
  - `NLIScorer` クラス（mDeBERTa-v3ラッパー）
  - `compute_nlc_score()` — 文分割 + NLI行列 + 集約
  - `check_coverage()` — 引用番号とエビデンスの対応チェック

### 変更
- `ai_agent/fact_checker.py`
  - `verify_and_synthesize`: プロンプトから `nlc_score` 自己出力指示を削除
  - `process_article`: NLIScorer で外部算出、measure_conductivity を削除
  - ステータス判定を5段階に変更
- `ai_agent/requirements.txt`
  - `torch` (CPU版), `transformers`, `sentence-transformers` 追加

### Backend変更（最小限）
- ステータスのenum値追加 (`likely_correct`, `uncertain`, `likely_incorrect`, `refuted`)
- `conductivity` カラムは当面nullable維持、将来削除（P5と連動）

---

## 5. 依存パッケージの追加

```bash
# CPU版PyTorch (Windowsで軽量)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers sentence-transformers
```

CPU版PyTorch: ~200MB (GPU版の1/10以下)

---

## 6. リスクと緩和策

| リスク | 影響 | 緩和策 |
|--------|------|--------|
| mDeBERTaの日本語SAP専門用語精度が不十分 | スコアが不正確 | Gemini APIフォールバック（低確信度ペアのみ） |
| 初回モデルロードに数秒 | 起動遅延 | アプリ起動時に1回だけロード |
| 512トークン入力制限 | 長文エビデンスの切り詰め | e5-smallで事前フィルタリング |
| 多段階分類のDB/フロントエンド対応 | 改修範囲拡大 | 初期は3段階維持、内部5段階→外部3段階マッピング |
