from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator

import extract
import fetch

app = FastAPI()


class IngestRequest(BaseModel):
    text: str | None = Field(default=None, min_length=1)
    url: str | None = None

    @model_validator(mode="after")
    def exactly_one(self):
        if (self.text is None) == (self.url is None):
            raise ValueError("provide exactly one of 'text' or 'url'")
        return self


@app.get("/health")
def health():
    return {"status": "ok"}


MAX_INPUT_CHARS = 20_000


@app.post("/ingest")
def ingest(req: IngestRequest):
    if req.url:
        try:
            text, resolved = fetch.fetch_document(req.url)
        except fetch.FetchError as e:
            raise HTTPException(status_code=e.status, detail=str(e)) from e
        source = resolved
        if not text:
            raise HTTPException(
                status_code=422,
                detail="no text could be extracted (scanned PDF or JavaScript-only page)",
            )
    else:
        text = req.text
        source = None

    text, truncated = fetch.truncate(text, MAX_INPUT_CHARS)

    try:
        data, problems, _ = extract.run(text, source=source)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    return {
        "problems": problems,
        "data": data,
        "meta": {"chars_used": len(text), "truncated": truncated},
    }
