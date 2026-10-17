import httpx
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


@app.post("/ingest")
def ingest(req: IngestRequest):
    if req.url:
        try:
            html, resolved = fetch.fetch_url(req.url)
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502, detail=f"could not fetch {req.url}: {e}"
            ) from e
        text = fetch.extract_text(html)
        source = resolved
    else:
        text = req.text
        source = None

    try:
        data, problems, _ = extract.run(text, source=source)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return {"problems": problems, "data": data}
