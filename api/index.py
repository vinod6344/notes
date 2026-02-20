from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Notes App Working Successfully 🚀"}