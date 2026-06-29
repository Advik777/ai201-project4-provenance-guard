# Provenance Guard

A backend system for classifying creative work as human or AI-generated, featuring ensemble detection and an appeals workflow.

## Transparency Labels
> **High-Confidence AI:** "This content has been identified as AI-generated with high certainty. It likely lacks original human authorship."
>
> **High-Confidence Human:** "This content has been verified as human-authored with high confidence. It shows strong markers of original creative work."
>
> **Uncertain:** "The origin of this content is unclear. Our analysis detected a mix of signals that suggest it may contain AI-generated elements or heavy AI assistance."

## Confidence Scoring & Ensemble Strategy
We use a weighted average of three signals:
1. **Groq LLM Signal (50%):** Semantic analysis using llama-3.3-70b-versatile.
2. **Stylometric Variance (25%):** Measures sentence length consistency.
3. **Vocabulary Richness (25%):** Analyzes the Type-Token Ratio (TTR).

**Thresholds:**
- **0.0 - 0.40:** High-Confidence Human
- **0.41 - 0.79:** Uncertain
- **0.80 - 1.0:** High-Confidence AI

## Production Safety
- **Rate Limiting:** 10 requests per minute. I chose this to allow creators to submit several drafts while preventing automated scripts from brute-forcing the model.
- **Audit Logging:** SQLite-based structured logs for every decision.

## Stretch Features Implemented
- **Ensemble Detection:** 3-signal weighted pipeline.
- **Provenance Certificate:** A "Verified Human" credential system.
- **Analytics Dashboard:** Real-time metrics via /analytics.
- **Multi-modal Support:** Support for text and image metadata analysis.

## Audit Log Evidence
```json
{
  "entries": [
    {
      "attribution": "uncertain",
      "confidence": 0.52,
      "content_id": "f41f05ee-05d7-43a6-ad40-89ec26a816c8",
      "creator_id": "advik",
      "llm_score": 0.64,
      "signals": "groq=0.6400; stylometric=0.7917; vocabulary=0.0000",
      "status": "classified",
      "timestamp": "2026-06-28T22:08:49.575616Z"
    },
    {
      "attribution": "uncertain",
      "confidence": 0.38,
      "content_id": "ac52cc18-c38a-4c0a-a6bd-415bd49dd8ff",
      "creator_id": "tester",
      "llm_score": 0.5,
      "signals": "groq=0.5000; stylometric=0.5000; vocabulary=0.0000",
      "status": "under_review",
      "timestamp": "2026-06-28T22:07:21.429661Z"
    },
    {
      "attribution": "uncertain",
      "confidence": 0.32,
      "content_id": "7f151969-b944-46aa-8878-15560ac39294",
      "creator_id": "advik_final_test",
      "llm_score": 0.64,
      "signals": "groq=0.6400; stylometric=0.0000; vocabulary=0.0000",
      "status": "classified",
      "timestamp": "2026-06-28T22:43:39.759086Z"
    }
  ]
}

## Rate Limit Evidence
I implemented a rate limit of 10 requests per minute to prevent automated "brute-force" attempts to bypass the detection model. Below is the output of a test script sending 12 rapid requests:

200
200
200
200
200
200
200
200
200
200
429
429
}