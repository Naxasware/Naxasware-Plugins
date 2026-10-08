# AI workflow architecture

Use when any step involves a language or other AI model, including RAG.

## Contents
1. Do you need AI here?
2. AI architecture components
3. Model selection criteria
4. AI decision specification
5. Confidence, validation and fallback
6. RAG workflows
7. Evaluation

## 1. Do you need AI here?

Use deterministic logic when the rule can be written down and the input is structured. Use AI where it adds real value: classification of free text, extraction from unstructured documents, summarization, generation, semantic matching, natural-language interaction, decision assistance. If you can state the rule in a sentence an engineer could code, it is not an AI step. Record the reason for each AI step as a requirement or driver reference; "it's an AI project" is not a reason.

## 2. Components

Identify only what the workflow needs: model, provider, gateway (if routing/limits/logging across models is needed), prompt layer, structured output, context, tools, memory, retrieval, guardrails, validation, evaluation, observability, fallback. Each added component needs a reason; a single classification call usually needs only model + prompt + schema + validation + fallback.

## 3. Model selection criteria

Reasoning capability, latency, cost, context window, structured-output support, tool-calling support, multimodal need, privacy/data-residency terms, availability, reliability. Choose the **smallest class of model that meets the measured quality bar**, validated against your own evaluation set. Never pick a model because it is popular. Model names, prices and limits change quickly: state requirements and candidate classes, mark specifics `REQUIRES VALIDATION`, and don't quote pricing you haven't verified.

## 4. AI decision specification

For each AI decision (`DEC-`), specify: purpose of the prompt, input (and what is excluded, e.g. PII), output schema (enumerated labels or typed JSON, not free text), confidence handling, validation, fallback, human escalation. Example:

```text
DEC-001  Is the lead qualified?
Input: lead form fields (no free-text PII beyond company/role)
Method: rule pre-filter, then LLM classification for ambiguous cases
Output: {label: qualified|unqualified|review, reason: string<=200 chars, signals: string[]}
Confidence: model-reported scores are not calibrated; use rule agreement + label=review as the low-confidence path
Validation: schema check; label in enum; reason non-empty
Fallback: on invalid output retry once, then route to human review
```

## 5. Confidence, validation and fallback

- Treat model output as untrusted input. Validate schema and value ranges deterministically before any action.
- Self-reported confidence is weak evidence. Prefer measurable signals: agreement between a rule and the model, agreement across two prompts or models, retrieval score thresholds, explicit `review`/`unknown` labels, calibration against a labeled set.
- Fallback ladder: retry with a repair prompt (bounded) → simpler/alternative path → human review → fail safely. Define which applies to which error.
- Keep AI output from directly triggering irreversible actions without a validation or approval gate.

## 6. RAG workflows

Pipeline: query → query processing → retrieval → filtering/reranking → context construction → LLM → validation → response.

Add RAG only when answers must come from a body of documents that is too large or too changeable to place in the prompt, or must be grounded and citable. Decide: source documents and ownership, update frequency (and re-indexing trigger), chunking approach, metadata and access control (retrieval must respect the asker's permissions — a classic leak), retrieval method (keyword, vector, hybrid — vector database only if justified by scale or semantic need), reranking, how many chunks fit the context, citation behavior, and what to answer when nothing relevant is retrieved ("I don't know" path). Evaluate retrieval separately from generation.

## 7. Evaluation

Define before building: accuracy/relevance on a labeled set, structured-output validity rate, hallucination or unsupported-claim rate, tool selection accuracy (if tools), task completion, refusal correctness, latency, cost per run. Use deterministic checks wherever possible (schema, enum, regex, reference lookup) and reserve model-based grading for what can't be checked mechanically — and spot-check the grader. Keep a regression set; re-run on every prompt, model or retrieval change. Test types are in `workflow-testing.md`.
