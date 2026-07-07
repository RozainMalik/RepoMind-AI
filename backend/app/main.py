from fastapi import FastAPI

app = FastAPI(title="RepoMind AI")

@app.get("/")
def root():
    return {"message": "RepoMind AI Backend"}
