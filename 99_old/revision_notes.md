# Revision notes — paper_ijai.tex → paper_ijai_v2.tex

Reference: Ikram et al. (2026), *Data and Information Management* 10, 100122 (Elsevier).
Target style: full Elsevier / DIM house style. Revision depth: deep.

---

## 0. Important context: the reference is a different *kind* of paper

The reference is a **systematic literature review** in an **information-science** journal; your paper is an **empirical deep-learning** study for **agriculture**. So the reference's *content structure* (PRISMA, research questions, meta-analysis, thematic synthesis) does **not** transfer. What transfers is the journal's **house style**, and that is what was applied:

- author–year citations `(Author, Year)` instead of IEEE `[1]`;
- single-paragraph unstructured abstract;
- sentence-case, numbered section headings;
- CRediT authorship statement + declarations block (Ethics / Generative AI / Funding / Competing interest);
- formal, hedged academic prose.

> ⚠️ **Venue fit:** *Data and Information Management* publishes information-management / information-science research, not agricultural CV. If your real target is a high-tech agriculture venue, keep this format as a *quality template* but pick an agriculture journal (e.g., *Computers and Electronics in Agriculture*, *Frontiers in Plant Science*, *Plant Methods*, *Smart Agricultural Technology*). Decide the true venue before final submission — it changes the reference style back to numeric for some of them.

---

## 1. Structural comparison (your original vs. reference standard)

| Element | Your original | Reference standard | Action taken |
|---|---|---|---|
| **Abstract** | Good single paragraph, results-heavy | Single paragraph: context → gap → method → results → contribution → limitation | Rewrote to open with the agronomic problem and annotation-cost gap before method/results |
| **Citations** | IEEE numeric `\cite` + `cite` package | Elsevier author–year | Converted to `natbib` author–year; `\citep`/`\citet` |
| **Headings** | ALL-CAPS, manual | Sentence case, auto-numbered | Retitled + `titlesec`; "METHODOLOGY" → "Materials and methods" |
| **Introduction** | 3 challenges + contributions, thin motivation | Extended motivation, explicit gap, sharp contributions, roadmap | Deepened motivation (economics, why localization matters), sharpened the two-gap framing, kept 4 contributions |
| **Related work** | 4 short subsections, few citations | Deeper synthesis + explicit positioning | Expanded each subsection; **added "Positioning of this work"** para stating the gap you fill |
| **Method** | Solid, but "V1/V2/V3" naming is opaque | Clear staged narrative | Reorganised into Stage 1–4 with explicit sub-headings; clarified which config = V1/V2/V3 |
| **Results** | Strong tables, honest caveats | Discussion woven around tables | Kept every number; tightened prose; promoted the caveat and SAM-expansion to first-class subsections |
| **Limitations** | Scattered across sections | Usually a dedicated block | **Added a dedicated "Limitations" subsection** consolidating all four |
| **Conclusion** | Enumerated findings + future work | Prose synthesis + directions | Converted to flowing prose; kept all findings and 5 future directions |
| **House-keeping** | None | CRediT + Ethics + GenAI + Funding + Competing interest | **Added all**, matching the reference verbatim in structure |

---

## 2. Key changes — what / why (reviewer's lens)

| # | Where | What changed | Why a reviewer scores it higher |
|---|---|---|---|
| 1 | Title | More descriptive, method-forward, sentence case | Signals contribution and scope at a glance; matches Elsevier norms |
| 2 | Abstract | Leads with the agronomic problem + annotation-cost gap, then method/results/limitation | Reviewers judge relevance in the first two sentences; a problem-first abstract reads as motivated, not just a results dump |
| 3 | Citations → author–year | All `\cite` → `\citep/\citet`; alphabetical Elsevier reference list | Matches target journal; author–year lets reviewers recognise the literature without flipping pages |
| 4 | Introduction | Explicit "two gaps" (classification-only; annotation cost) + roadmap | A crisp, named gap is the single strongest driver of a positive intro review |
| 5 | Related work | Added synthesis + "Positioning of this work" | Shows command of the field and defends novelty pre-emptively — reviewers look for this |
| 6 | Method | Stage-numbered narrative, clarified V1/V2/V3 mapping | Reduces reader confusion (a top-3 cause of "major revision"); improves reproducibility |
| 7 | Caveat + SAM expansion | Promoted to dedicated subsections; added a two-sided guard fix | Transparent negative results build trust and read as scientific maturity, not weakness |
| 8 | Limitations | Consolidated into one subsection tied to future work | Reviewers penalise hidden limitations; a candid block usually *earns* credit |
| 9 | CRediT + declarations | Added full block | Mandatory at Elsevier; missing them triggers a desk-return before review |
| 10 | Prose | Hedged, formal, active where clear | Matches journal register; avoids overclaiming, which reviewers punish |

---

## 3. Weak points to strengthen before submission

**Highest priority (likely reviewer blockers):**

1. **No ground-truth masks.** This is your central limitation — a reviewer will ask for it. Manually annotate 50–100 test images (even one annotator) to report *absolute* IoU/Dice. Without it, all segmentation numbers remain relative to pseudo-labels.
2. **No segmentation baselines.** You compare only your own V1/V2/V3. Add at least one external baseline (e.g., plain U-Net, DeepLabv3+, or a CAM-only weakly-supervised method) on the same split so the contribution is benchmarked, not just self-referential.
3. **No statistical rigour.** All metrics are single-run point estimates. Report mean ± std over ≥3 seeds and, ideally, a significance test for the V2→V3 gain (+21.5% IoU) so it is not dismissed as noise.
4. **Dataset provenance is thin.** "Collected from plantations in Southeast Asia" needs specifics: where, when, camera/conditions, and whether it is public or will be released. Reproducibility reviewers require this.

**Medium priority:**

5. **Related work is under-cited.** Only ~14 references, all reused from your original. Add recent (2022–2025) weakly-supervised plant-disease-segmentation and SAM-in-agriculture papers, and a durian-specific reference if one exists. Aim for 25–35 references. *(I did not invent citations — add real ones you verify.)*
6. **Class imbalance / confusion not analysed.** The confusion between Algal and Phomopsis spots is mentioned but not quantified or addressed. A short paragraph (or per-pair error rates) would close the loop.
7. **Ablation of the fusion weights.** The 0.6/0.4 fine/coarse split and the per-class percentages look hand-tuned. A small ablation, or a sentence on how they were chosen, pre-empts "why these values?".
8. **SAM prompt-design ablation.** You fix 5 FG + 3 BG points and 30-px dilation. One sensitivity table would strengthen Stage 3.

**Low priority / housekeeping:**

9. **Fill in the Generative AI statement** with the actual tools used (the reference discloses Grammarly). Leaving the template is a desk-check risk.
10. **Verify CRediT roles** — I inserted a plausible split; confirm it matches reality.
11. **Confirm funding/competing-interest** statements are accurate for your institutions.
12. **Figure quality:** ensure all PNGs are ≥300 dpi and legible at column width; several are referenced at `\textwidth`.
13. **Consider renaming V1/V2/V3** to descriptive tags (e.g., "Baseline", "GradCAM++", "SAM-refined") throughout for readability — currently only clarified at first mention.

---

## 4. What was preserved unchanged

All quantitative content: 97.52% accuracy, per-class scores, coverage stats, IoU/Dice tables (V1 0.7671 / V2 0.5135 / V3 0.6239), the +21.5% figure, SAM expansion percentages, training-dynamics checkpoints, timings, the TikZ pipeline figure, and all seven figure references. **No numbers were altered or invented.**
