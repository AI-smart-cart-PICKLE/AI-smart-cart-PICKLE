from fastapi import FastAPI
import logging

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World from Smart Cart Backend"}

@app.get("/health")
def health():
    return {"status": "ok"}
