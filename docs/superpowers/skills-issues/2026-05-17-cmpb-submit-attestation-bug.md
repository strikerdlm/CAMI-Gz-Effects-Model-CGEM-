# `cmpb-submit` skill — AI non-use attestation bug

**Skill:** `~/.claude/skills/cmpb-submit/SKILL.md`
**Reported:** 2026-05-17
**Reporter:** Diego Malpica (during CGEM CMPB-then-BSPC pivot, session 2026-05-17)
**Status:** Fixed in-place 2026-05-17 (8 edits applied via the CGEM working session; not committed because the skill directory is not inside a git repository).

## Bug

The skill's pre-2026-05-17 version of `SKILL.md` claimed that the CMPB cover letter must contain a verbatim NON-USE attestation of generative AI:

> "The authors specifically state that they have not used generative AI in the preparation of this manuscript. ChatGPT, Large Language Models, and any other generative AI programs have not been used as a replacement for original thought or to perform activities that would normally be the responsibility of the authors (e.g., developing hypotheses, selecting and interpreting statistical tests, writing the abstract, formatting the article). Generative AI has not been used to create images, multimedia, or graphic elements. Standard referencing software tools used in the normal course of manuscript preparation are not considered generative AI."

The mandatory-attestation language appeared in eight places: the cover-letter Requirements section (item 5), the cover-letter template, the pre-submission checklist (`status` mode), the formatting rules table, the compliance audit (`check` mode), the rules quick-reference table (`rules` mode), the peer-review mode (`review` mode) compliance row, and the portal upload walkthrough Step 8.

## Why it's wrong

Independent verification (2026-05-17, two agent runs against the live CMPB Guide for Authors and the Elsevier publisher-wide policy):

1. **Live CMPB Guide for Authors** scraped 2026-05-17: carries only Elsevier's standard *disclosure-if-used* clause — *"Authors must declare the use of generative AI in the manuscript preparation process upon submission of the paper. […] If you have nothing to disclose, you do not need to add a statement."*
2. **Elsevier publisher-wide policy** (updated September 2025, `https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals`): identical *disclosure-if-used* language; AI declaration belongs in the **manuscript** (before References), not the cover letter.
3. **Elsevier cover-letter guidance** (updated 2025-10-09, `https://www.elsevier.support/publishing/answer/what-should-be-included-in-a-cover-letter`): the cover letter "should not include funding information, author declarations, or suggested or opposed reviewers" — author declarations are precisely what an AI attestation is.
4. **Exact-phrase search** for the skill's verbatim block ("replacement for original thought", "developing hypotheses … formatting the article", "Standard referencing software tools used in the normal course"): zero hits across Tavily and Brave on 2026-05-17. The block does not appear in any indexed Elsevier, CMPB, special-issue, Editorial Manager, or third-party source.

The skill's self-described provenance is *"verified via secondary sources 2026-05-01"* — i.e., never directly verified against the live Guide.

## Workspace impact (this manuscript)

The CGEM CMPB pivot spec (`docs/superpowers/specs/2026-05-17-cgem-cmpb-pivot-design.md`) explicitly waives the skill's `check`-mode FAIL on this clause. The cover letter at `manuscripts/cmpb/src/cover_letter_cmpb.md` (later renamed to `manuscripts/bspc/src/cover_letter_bspc.md` after the CMPB → BSPC pivot) does **not** contain the verbatim block. This is policy-compliant per spec §5 and per Elsevier's actual *disclosure-if-used* policy under Diego's local "nothing to disclose, no statement" stance.

After the CMPB → BSPC re-pivot (CMPB cap mismatch surfaced; spec amendment in the same docs/superpowers/specs/ file), the bug remains relevant because:
1. BSPC follows the same Elsevier publisher-wide AI policy.
2. The cmpb-submit docx-builder is being adapted to build the BSPC submission package — its underlying Python library is journal-agnostic for formatting, so the docx-build mechanics carry over.
3. Future submissions to any other Elsevier journal in this workspace will benefit from the corrected skill.

## Upstream fix

The skill itself was edited in-place on 2026-05-17. Eight sections were updated to replace the mandatory non-use attestation with Elsevier's actual *disclosure-if-used* policy:

| Section | Change |
|---|---|
| Cover Letter Requirements (item 5) | "Generative AI non-use attestation" → "Generative AI disclosure (only if AI was used)" |
| Cover letter template (AI line) | Verbatim attestation block → conditional placeholder with omission-allowed semantics |
| Formatting Rules table — Generative AI row | "Cover letter must contain a verbatim attestation…" → "Disclosure-if-used (Elsevier publisher-wide policy, verified 2026-05-17): in-manuscript declaration before References; no statement if nothing to disclose" |
| Pre-submission checklist | Verbatim-attestation check → disclosure-if-used compliance check |
| Rules quick-reference table — Generative AI block | Same correction |
| Peer-review mode compliance row | Verbatim-attestation row → disclosure-if-used compliance check |
| Portal upload walkthrough Step 8 (AI declaration question) | "Answer with the verbatim non-use attestation" → "Answer per Elsevier disclosure-if-used policy; leave empty if nothing to disclose" |
| Changelog | New `1.2.0 — 2026-05-17` entry citing the verification trail and the 8 edited sections |

No commit/push was made because `/root/.claude/skills/cmpb-submit/` is not inside a git repository (the only git repo anywhere under `/root/.claude/` is `/root/.claude/plugins/marketplaces/cli-anything/.git`, which is unrelated). The skill edits are in-place on the local filesystem and persist across sessions; if the upstream skill catalog publishes a new version that overwrites these local edits, this bug report serves as the canonical workspace record of the fix.

## How to use this report

- **Future Elsevier submissions in this workspace:** read this report before invoking `cmpb-submit`. The skill now (post-fix) emits disclosure-if-used language. If a future skill update reverts the AI-policy text, the verification trail above explains why the local edit was correct.
- **Adapting cmpb-submit for non-CMPB Elsevier journals (e.g., BSPC):** the docx-builder mechanics (line-numbering XML, double-spacing XML, Highlights 85-char validation, Vancouver reference style, structured-abstract handling) are journal-agnostic. The only journal-specific change is the cover-letter template's EiC address and scope-framing.
- **For CMPB submissions specifically:** the skill's `cover-letter` mode now emits the correct disclosure-if-used language. Use `docx` mode to build the portal package; `check` mode no longer FAILs on the attestation clause.

## Cross-references

- Spec: `docs/superpowers/specs/2026-05-17-cgem-cmpb-pivot-design.md`
- Plan: `docs/superpowers/plans/2026-05-17-cgem-cmpb-pivot.md`
- 2026-05-12 scout (pre-CMPB-pivot): `docs/publication/2026-05-12_journal-scout_cgem-emulator.md`
- 2026-05-17 scout (post-IJNMBE-rejection, AI-policy-filtered): `docs/publication/2026-05-17_journal-scout_cgem-emulator.md`
- OSF amendment: `docs/publication/osf_amendment_2026-05-17.md`
