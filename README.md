#English Agent
Turns messy English learning materual -- articles, PDFs, raw notes -- into a structured  knowledge base.

**Inout:** a URL, a PDF, or raw text.
**Output:** structured entries: key sentences, vocabulary, takeaways.

## Status

Week 1 -- a running FastAPI service with a '/health' endpoint.

## Run locally

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    uvicorn main:aoo --reload

Then open http://127.0.0.1:8000/docs