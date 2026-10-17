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
            html, resolved = fetch.fetch_url(req.url)
        except fetch.FetchError as e:
            raise HTTPException(status_code=e.status, detail=str(e)) from e
        text = fetch.extract_text(html)
        source = resolved
        if not text:
            raise HTTPException(
                status_code=422,
                detail="no text could be extracted (the page may need JavaScript)",
            )
    else:
        text = req.text
        source = None

    if len(text) > MAX_INPUT_CHARS:
        raise HTTPException(
            status_code=422,
            detail=f"input is {len(text)} chars, over the {MAX_INPUT_CHARS} limit",
        )

    try:
        data, problems, _ = extract.run(text, source=source)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return {"problems": problems, "data": data}
