from fastapi import FastAPI
import time

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Business logic service: processes data"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/process")
def process(payload: dict):
    time.sleep(2)
    return {"original": payload, "processed": True}