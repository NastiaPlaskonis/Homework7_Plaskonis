from fastapi import FastAPI, Request
from typing import Any


app = FastAPI()
database = []

@app.get("/")
def root():
    return {"message": "Database Service: stores data"}

@app.get("/health")
def health():
    return {"status": "OK"}


@app.post("/save")
async def save(request: Request):
    data = await request.json()
    database.append(data)
    return {"status": "saved", "data": data}

@app.get("/get")
def get():
    return {"data": database}