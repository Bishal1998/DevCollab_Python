from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"detail" : "Welcome to DevCollab!"}