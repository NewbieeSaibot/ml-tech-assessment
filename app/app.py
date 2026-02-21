from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.adapters.simple_in_memory_database import SimpleInMemoryDatabase
from app.routes.transcript_analyzer import router as transcript_router
import pydantic


@asynccontextmanager
async def lifespan(app_: FastAPI):
    app_.state.db = SimpleInMemoryDatabase[pydantic.BaseModel]()
    yield


app = FastAPI(
    title="Transcription Analyzer API",
    lifespan=lifespan
)


app.include_router(
    transcript_router,
    prefix="/transcripts",
    tags=["Transcript Analyzer"]
)
