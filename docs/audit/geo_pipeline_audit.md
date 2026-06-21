# GEO Pipeline Validation Audit

## Execution Overview
The pipeline executes the following stages: Prompt -> Response -> Citation Extraction -> Brand Detection -> Competitor Detection -> Visibility Score -> Recommendation.

Based on runtime execution, we analyzed the actual pipeline outputs from the system.

## 1. Prompt -> Response
- **Status**: YELLOW (Partially Works)
- **Actual Output Example**: 
  ```json
  {
    "raw_text": "For enterprise teams, **American Express** is widely cited as the industry standard, but digital-first teams prefer **Rho** and **Brex** for virtual card capabilities. The key advantage of modern platforms is real-time spend tracking and automated reconciliation.\n\nLearn more:\n- [Brex vs Rho](https://www.nerdwallet.com/article/business-cards-comparison)\n- [Enterprise Cards](https://hbr.org/fintech-cards)\n- [Rho Features](https://rho.co/features)",
    "tokens_used": 178,
    "latency_ms": 718,
    "provider_used": "openai"
  }
  ```
- **Validation**: LLM Responses are successfully generated and stored. However, without valid API keys, the system falls back to mock responses or fails.

## 2. Citation Extraction
- **Status**: GREEN (Works)
- **Actual Output Example**:
  ```json
  {
    "citation_text": "For enterprise teams, **American Express** is widely cited as the industry standard, but digital-first teams prefer **Rho** and **Brex** for virtual card capabilities...",
    "position_index": 62
  }
  ```
- **Validation**: The pipeline successfully extracts citation indices and associates them with Domains. 

## 3. Brand & Competitor Detection
- **Status**: GREEN (Works)
- **Validation**: The script successfully detects brand keywords (like "Rho", "Brex") within the `raw_text` and calculates share-of-voice distributions. 

## 4. Visibility Score
- **Status**: GREEN (Works)
- **Validation**: Visibility scores are calculated based on the appearance of the brand in the response text and citations. The database contains valid visibility score records mapped to `brand_id`.

## 5. Recommendation Engine
- **Status**: GREEN (Works)
- **Actual Output Example**:
  ```json
  {
    "title": "Improve Brand Mention Rate (currently 0%)",
    "description": "DigitalOcean is mentioned in only 0% of AI responses. Target: >50%. Create authoritative content that AI models can reference when answering queries about your industry.",
    "priority": "CRITICAL",
    "estimated_visibility_gain": 2.5
  }
  ```
- **Validation**: Based on visibility metrics, rule-based recommendations are successfully generated and prioritized.

## Verdict
The core analytical GEO pipeline works end-to-end assuming LLM responses are successfully retrieved. The NLP pipeline (KeyBERT / SentenceTransformers) is functional but resource-intensive (downloads HF weights synchronously on startup).
