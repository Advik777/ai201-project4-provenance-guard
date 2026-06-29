# Project Planning: Provenance Guard

## Architecture
```mermaid
graph TD
    A[User Submission] --> B{Multi-modal Gateway}
    B -->|Text/Image Metadata| C[Ensemble Engine]
    C --> D[Signal 1: Groq LLM Semantic Check]
    C --> E[Signal 2: Stylometric Variance]
    C --> F[Signal 3: Vocabulary Diversity]
    D & E & F --> G[Weighted Scoring Logic]
    G --> H[Transparency Label Generator]
    H --> I[SQLite Audit Log]
    H --> J[Final API Response]
    K[Appeals Endpoint] --> I
    L[Analytics Dashboard] --> I


Narrative: 
My system uses a multi modal gateway that handles both standard text and image metadata descriptions. These inputs are processed by an ensemble engine that calculates a weighted score from three independent signals. All results, including raw scores and the final transparency label, are stored in a structured SQLite audit log. This log serves as the single source of truth for the appeals workflow and the real-time analytics dashboard.

1. Detection Signals
Signal 1: Groq LLM (Semantic): Uses llama-3.3-70b-versatile to assess holistic style. Output: A float between 0.0 and 1.0 (1.0 = AI).

Signal 2: Stylometric Variance (Structural): A Python heuristic measuring sentence length variance. Output: A float (0-1) where 1.0 indicates extremely low variance (likely AI).

Signal 3: Type-Token Ratio (Structural): Measures vocabulary diversity. Output: A float (0-1) where 1.0 indicates low vocabulary diversity (likely AI).

Combination Logic: We combine these into a single calibrated score using a weighted average: Final Score = (Groq * 0.5) + (Variance * 0.25) + (TTR * 0.25).


2. Uncertainty Representation
Calibrated Score Meaning: A score of 0.6 represents "Mixed Signals." This specifically occurs when the LLM detects AI-like semantic patterns, but the structural heuristics (like high sentence variance) suggest human-like creative "burstiness."

Mapping: Raw signal scores are normalized to a 0-1 range before being averaged.

Thresholds:
0.0 - 0.40: Likely Human
0.41 - 0.79: Uncertain
0.80 - 1.0: Likely AI


3. Transparency Label Design
High-Confidence AI: "This content has been identified as AI-generated with high certainty.It likely lacks original human authorship."

High-Confidence Human: "This content has been verified as human-authored with high confidence. It shows strong markers of original creative work."

Uncertain: "The origin of this content is unclear. Our analysis detected a mix of signals that suggest it may contain AI-generated elements or heavy AI assistance."


4. Appeals Workflow
Submission: Creators provide content_id and creator_reasoning.

System Action: Status updates to under_review in the AuditLog. Reasoning is stored in the Appeals table.


5. Anticipated Edge Cases
Case 1 (Repetitive Poetry): Intentional human repetition (villanelles) triggers low TTR, leading to false AI flags.

Case 2 (Technical Manuals): Uniform sentence lengths in technical docs trigger stylometric AI markers.


## AI Tool Plan

M3: Provided Detection Signals + Architecture. Requested Flask skeleton + Groq Signal 1. Verified via curl.

M4: Provided Uncertainty Representation. Requested Signal 2 & 3 math. Verified with AI vs Human text.

M5: Provided Label Design + Appeals Workflow. Requested label logic + /appeal endpoint. Verified DB status updates.

AI Request: "Implement the Signal 2 (Stylometric Variance) and Signal 3 (TTR) functions, and write the weighted scoring logic to combine all three signals into a calibrated score."

Verification: Check if scores vary meaningfully between a clearly AI-generated paragraph and a highly creative, varied human text.


Stretch Features Plan
Ensemble Detection: 3-signal weighted pipeline (implemented above).

Provenance Certificate: /verify endpoint for "Verified Human" credentials.

Analytics Dashboard: /analytics route for real-time system metrics.

Multi-modal Support: Analysis for image_description metadata.

