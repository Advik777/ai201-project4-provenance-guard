Provenance Guard

Provenance Guard is a backend system designed to classify creative content as human-authored or AI-generated. It uses a multi-signal ensemble engine to provide transparency labels to users and a robust appeals workflow for creators.

Architecture Overview
The system follows a structured pipeline for every submission:

Input Gateway: Accepts text-based content and metadata via a REST API.

Ensemble Engine: Routes the content to three independent detection signals simultaneously.

Weighted Scoring: Aggregates raw signal outputs into a single calibrated confidence score.

Label Generation: Maps the final score to one of three transparency labels.

Audit Logging: Records the entire decision process (scores, timestamps, labels) in a SQLite database.

Appeals/Analytics: Powers a creator-facing appeal system and a real-time analytics dashboard.


Detection Signals
I chose an ensemble of three distinct signals to balance semantic understanding with structural statistical analysis:

Signal 1: Groq LLM (Semantic): Uses llama-3.3-70b-versatile to assess holistic style and coherence. It is excellent at catching AI vibes but can be tricked by highly sophisticated prompting.

Signal 2: Stylometric Variance (Structural): Measures sentence length variation. AI text tends to be statistically uniform, while human writing is "bursty." It misses cases where AI is specifically prompted to vary sentence structure.

Signal 3: Vocabulary Richness (Structural): Analyzes the Type-Token Ratio (unique words vs. total words). It catches the repetitive, safe vocabulary common in base LLM outputs but may flag technical human writing as AI.


Confidence Scoring
Signals are combined using a weighted average: (Groq * 0.5) + (Variance * 0.25) + (TTR * 0.25). This ensures the LLM's semantic insight carries the most weight while being "checked" by structural heuristics.

Validation Examples:

High-Confidence AI Submission:
Input: "Artificial intelligence represents a transformative paradigm shift in modern society..."

Final Score: 0.66 (Note: Landed in 'Uncertain' due to high structural variety in the test text, demonstrating the system's bias toward avoiding false positives).

High-Confidence Human Submission:

Input: "ok so i finally tried that new ramen place..."

Final Score: 0.32 (Correctly categorized as Human).


Transparency Labels
The following verbatim labels are displayed based on thresholds:

High-Confidence AI (>= 0.80): "This content has been identified as AI-generated with high certainty. It likely lacks original human authorship."

High-Confidence Human (<= 0.40): "This content has been verified as human-authored with high confidence. It shows strong markers of original creative work."

Uncertain (0.41 - 0.79): "The origin of this content is unclear. Our analysis detected a mix of signals that suggest it may contain AI-generated elements or heavy AI assistance."


Rate Limiting
I implemented a limit of 10 requests per minute per IP.

Reasoning: This is high enough for a human creator to submit multiple drafts or chapters for analysis, but low enough to prevent automated scripts from "brute-forcing" the detection model by making tiny incremental changes to AI text until it passes as human.


Known Limitations
The system is likely to misclassify highly structured technical documentation. Because technical manuals require uniform sentence lengths and standardized, repetitive vocabulary, Signals 2 and 3 will produce high AI scores, potentially triggering an "AI" or "Uncertain" label for human-written technical work.


Spec Reflection
How the spec helped: The requirement to define "Uncertainty" in Milestone 2 forced me to realize that a binary 0.5 flip was insufficient. Designing the 0.6 "Mixed Signals" category in the spec made the implementation of the ensemble math much more logical.

Divergence: I diverged from the spec by widening the Human threshold. Initially, I planned for 0.0–0.20 to be human, but testing showed that casual human speech (like reviews) often scored around 0.30 due to simple vocabulary. I adjusted the threshold to 0.40 to better reflect real-world human writing.


AI Usage
1-  I directed the AI to generate the Python logic for sentence length variance and TTR. I overrode the initial normalization values because they were too sensitive, initially labeling professional human writing as AI.

2-  When I encountered a mismatch between my API and SQLite columns, I used AI to regenerate a synchronized database.py and app.py to ensure the content_id was handled consistently across the appeals workflow.

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

