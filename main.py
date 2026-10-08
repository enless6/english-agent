from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import extract

app = FastAPI()


class IngestRequest(BaseModel):
    text: str = Field(min_length=1, description="The English passage to process")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest(req: IngestRequest):
    try:
        data, problems, _ = extract.run(req.text)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return {"problems": problems, "data": data}
