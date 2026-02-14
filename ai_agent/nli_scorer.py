"""
NLI-based NLC Score Calculator for SAPJP-pedia Fact Checker.

Uses mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 to compute
entailment/neutral/contradiction scores between synthesized text
and evidence snippets. Replaces LLM self-scoring (P2).
"""

import re
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"

# Sentence split patterns
_JA_SPLIT = re.compile(r'(?<=[。！？])')
_EN_SPLIT = re.compile(r'(?<=[.!?])\s+')


class NLIScorer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        self.model.eval()
        # label order for this model: entailment=0, neutral=1, contradiction=2
        self.label_names = self.model.config.id2label
        print(f"[NLIScorer] Loaded model: {MODEL_NAME}")
        print(f"[NLIScorer] Labels: {self.label_names}")

    # ------------------------------------------------------------------
    # Core NLI inference
    # ------------------------------------------------------------------

    def score_pair(self, premise: str, hypothesis: str) -> dict:
        """Score a single premise-hypothesis pair.

        Returns dict with keys 'entailment', 'neutral', 'contradiction',
        each mapped to a probability [0, 1].
        """
        inputs = self.tokenizer(
            premise, hypothesis,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )
        with torch.no_grad():
            logits = self.model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0].tolist()

        result = {}
        for idx, prob in enumerate(probs):
            label = self.label_names[idx].lower()
            result[label] = prob
        return result

    def score_pairs_batch(self, pairs: list[tuple[str, str]]) -> list[dict]:
        """Score multiple premise-hypothesis pairs in a single batch.

        Args:
            pairs: List of (premise, hypothesis) tuples.

        Returns:
            List of dicts with 'entailment', 'neutral', 'contradiction'.
        """
        if not pairs:
            return []

        inputs = self.tokenizer(
            [p[0] for p in pairs],
            [p[1] for p in pairs],
            truncation=True,
            max_length=512,
            padding=True,
            return_tensors="pt",
        )
        with torch.no_grad():
            logits = self.model(**inputs).logits
        all_probs = torch.softmax(logits, dim=-1).tolist()

        results = []
        for probs in all_probs:
            result = {}
            for idx, prob in enumerate(probs):
                label = self.label_names[idx].lower()
                result[label] = prob
            results.append(result)
        return results

    # ------------------------------------------------------------------
    # Sentence splitting (SummaC-style)
    # ------------------------------------------------------------------

    def split_sentences(self, text: str) -> list[str]:
        """Split text into sentences.

        Handles Japanese (。！？) and English (.!? + space) delimiters.
        """
        # First try Japanese split
        parts = _JA_SPLIT.split(text)
        if len(parts) <= 1:
            # Fallback to English split
            parts = _EN_SPLIT.split(text)

        sentences = [s.strip() for s in parts if s.strip()]
        # Filter out very short fragments (< 5 chars)
        sentences = [s for s in sentences if len(s) >= 5]
        return sentences if sentences else [text.strip()]

    # ------------------------------------------------------------------
    # Main scoring pipeline
    # ------------------------------------------------------------------

    @staticmethod
    def _chunk_text(text: str, max_chars: int = 300) -> list[str]:
        """Split text into chunks of roughly max_chars, breaking at sentence boundaries."""
        chunks = []
        current = ""
        for part in re.split(r'(?<=[。！？.!?])\s*', text):
            if not part.strip():
                continue
            if len(current) + len(part) > max_chars and current:
                chunks.append(current.strip())
                current = part
            else:
                current += part
        if current.strip():
            chunks.append(current.strip())
        return chunks if chunks else [text[:max_chars]]

    def compute_nlc_score(self, synthesized_text: str, evidences: list) -> dict:
        """Compute NLC score for synthesized text against evidence list.

        Uses chunked evidence (not sentence-level) and batch inference
        to keep total NLI calls manageable (~sentences × evidence_count × ~3 chunks).

        Args:
            synthesized_text: The AI-synthesized article text.
            evidences: List of dicts with at least 'snippet' and 'pc1_score'.

        Returns:
            {
                "nlc_score": float,
                "details": [{"sentence": str, "max_entailment": float, ...}, ...],
                "has_contradiction": bool
            }
        """
        if not evidences or not synthesized_text.strip():
            return {"nlc_score": 0.0, "details": [], "has_contradiction": False}

        sentences = self.split_sentences(synthesized_text)

        # Filter: only use evidences that LLM cited (have a quote)
        # Uncited evidences are likely irrelevant and cause false contradictions
        quoted = [ev for ev in evidences if (ev.get("quote") or "").strip() and len((ev.get("quote") or "").strip()) >= 20]
        if not quoted:
            # Fallback: use snippet-based evidences if no quotes available
            quoted = [ev for ev in evidences if ev.get("snippet", "")]
        sorted_evidences = sorted(
            quoted,
            key=lambda ev: ev.get("pc1_score", 0.5),
            reverse=True,
        )[:5]

        evidence_chunks = []  # list of (chunk_text, pc1_score)
        for ev in sorted_evidences:
            quote = (ev.get("quote") or "").strip()
            if quote and len(quote) >= 20:
                chunk = quote[:500]  # quote is clean, allow longer
            else:
                chunk = ev["snippet"][:300]
            pc1 = ev.get("pc1_score", 0.5)
            evidence_chunks.append((chunk, pc1))

        if not evidence_chunks:
            return {"nlc_score": 0.0, "details": [], "has_contradiction": False}

        total_pairs = len(sentences) * len(evidence_chunks)
        print(f"  [NLI] {len(sentences)} sentences × {len(evidence_chunks)} chunks = {total_pairs} pairs")

        details = []
        has_contradiction = False

        for i, sent in enumerate(sentences):
            best_entailment = 0.0
            best_pc1 = 0.5
            worst_contradiction = 0.0

            for chunk_text, pc1 in evidence_chunks:
                scores = self.score_pair(chunk_text, sent)
                ent = scores.get("entailment", 0.0)
                con = scores.get("contradiction", 0.0)
                if ent > best_entailment:
                    best_entailment = ent
                    best_pc1 = pc1
                if con > worst_contradiction:
                    worst_contradiction = con

            if worst_contradiction > 0.7:
                has_contradiction = True

            # TODO: PC1ドメイン信頼度の重み付けは一時的に無効化（全URL=0.5問題の回避）
            weighted_score = best_entailment
            if worst_contradiction > 0.5:
                weighted_score *= (1.0 - worst_contradiction * 0.5)

            details.append({
                "sentence": sent[:100],
                "max_entailment": round(best_entailment, 4),
                "max_contradiction": round(worst_contradiction, 4),
                "pc1_weight": best_pc1,
                "weighted_score": round(weighted_score, 4),
            })

            print(f"  [NLI] {i + 1}/{len(sentences)}: ent={best_entailment:.3f} con={worst_contradiction:.3f} w={weighted_score:.3f}")

        # Citation coverage check
        citation_nums = set(int(m) for m in re.findall(r'\[(\d+)\]', synthesized_text))
        evidence_nums = set(ev.get("reference_num", 0) for ev in evidences)
        uncovered = citation_nums - evidence_nums
        coverage_penalty = 1.0 if not uncovered else max(0.8, 1.0 - 0.05 * len(uncovered))

        if details:
            avg_score = sum(d["weighted_score"] for d in details) / len(details)
        else:
            avg_score = 0.0

        nlc_score = round(avg_score * coverage_penalty, 4)

        print(f"  [NLI] Final NLC Score: {nlc_score} (contradiction: {has_contradiction})")

        return {
            "nlc_score": nlc_score,
            "details": details,
            "has_contradiction": has_contradiction,
        }

    # ------------------------------------------------------------------
    # Status classification (5-tier)
    # ------------------------------------------------------------------

    @staticmethod
    def determine_status(nlc_score: float) -> str:
        """Map NLC score to 5-tier status."""
        if nlc_score >= 0.85:
            return "verified"
        elif nlc_score >= 0.70:
            return "likely_correct"
        elif nlc_score >= 0.50:
            return "uncertain"
        elif nlc_score >= 0.30:
            return "likely_incorrect"
        else:
            return "refuted"
