from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.session import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"detail": "Welcome to DevCollab!"}
