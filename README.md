# English Agent
Turns messy English learning material -- articles, PDFs, raw notes -- into a structured knowledge base.

**Input:** a URL, a PDF, or raw text.
**Output:** structured entries: key sentences, vocabulary, takeaways.

## Status

Week 1 -- a running FastAPI service with a `/health` endpoint.
Week 2 -- English text goes in, structured study material (key sentences, vocabulary, takeaways) comes out as JSON.
Week 3 -- the pipeline became an endpoint: `POST /ingest` validates the model's output and retries it with feedback when validation fails; `test_validate.py` covers the validators offline, with no API calls.

## Run locally

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs

## Known issues

**Occasional Chinese characters in English fields.** The model sometimes emits a Chinese word inside an English sentence in `note` or `usage_note` (seen once: `how` 软件 engineers).
Measured 1 dirty sample out of 7 single-shot runs on one input -- too few to estimate the rate. `run()` retries with feedback, which usually clears it, and the API response reports any problems that survive. Deliberately not patched by prompting: verifying such a change would cost more calls than the defect is worth.
