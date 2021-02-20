from fastapi import FastAPI

backend = FastAPI()

@backend.get("/")
def home():
    return {"Result":"ok"}