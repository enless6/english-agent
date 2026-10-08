from fastapi import FastAPI
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
    data, problems, _ = extract.run(req.text)
    return {"problems": problems, "data": data}
