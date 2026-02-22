from fastapi import APIRouter, HTTPException, Query, Depends, Request
from pydantic import BaseModel
from typing import List
import asyncio

from app.adapters.openai import OpenAIAdapter
from app.adapters.simple_in_memory_database import SimpleInMemoryDatabase
from app.configurations import EnvConfigs
from app.models.transcript import TranscriptAnalysisDTO, TranscriptAnalysisResponse, BatchTranscriptRequest
from app.models.database import DBStatus, LoadStatus
from app.prompts import SYSTEM_PROMPT, RAW_USER_PROMPT


router = APIRouter()


def get_openai_adapter() -> OpenAIAdapter:
    return OpenAIAdapter(
        api_key=EnvConfigs().OPENAI_API_KEY,
        model=EnvConfigs().OPENAI_MODEL
    )


def get_db(request: Request) -> SimpleInMemoryDatabase[BaseModel]:
    return request.app.state.db


@router.get("/analyze", response_model=TranscriptAnalysisResponse)
def analyze_transcript(
    transcript: str = Query(..., description="Plain text transcript"),
    adapter: OpenAIAdapter = Depends(get_openai_adapter),
    db: SimpleInMemoryDatabase[BaseModel] = Depends(get_db),
):
    if not transcript or not transcript.strip():
        raise HTTPException(
            status_code=400,
            detail="Transcript cannot be empty"
        )

    user_prompt = RAW_USER_PROMPT.format(transcript=transcript)

    analysis = adapter.run_completion(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        dto=TranscriptAnalysisDTO,
    )

    store_status = db.store(analysis)

    if store_status.status != DBStatus.SUCCESS:
        raise HTTPException(
            status_code=500,
            detail=store_status.message or "Failed to store analysis"
        )

    return TranscriptAnalysisResponse(
        id=store_status.object_id,
        summary=analysis.summary,
        next_actions=analysis.next_actions,
    )


@router.get("/analysis/{analysis_id}", response_model=TranscriptAnalysisResponse)
def get_transcript_analysis(
    analysis_id: str,
    db: SimpleInMemoryDatabase = Depends(get_db),
):
    load_status: LoadStatus = db.load(analysis_id)

    if load_status.status == DBStatus.NOT_FOUND:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    if load_status.status == DBStatus.ERROR:
        raise HTTPException(
            status_code=500,
            detail=load_status.message or "Internal error",
        )

    analysis = load_status.data

    return TranscriptAnalysisResponse(
        id=analysis_id,
        summary=analysis.summary,
        next_actions=analysis.next_actions,
    )


@router.post("/analyze/batch", response_model=List[TranscriptAnalysisResponse])
async def analyze_multiple_transcripts(
    payload: BatchTranscriptRequest,
    adapter: OpenAIAdapter = Depends(get_openai_adapter),
    db: SimpleInMemoryDatabase = Depends(get_db),
):
    if not payload.transcripts:
        raise HTTPException(
            status_code=400,
            detail="Transcripts list cannot be empty",
        )

    async def process_single_transcript(transcript: str):
        if not transcript.strip():
            raise ValueError("Transcript cannot be empty")

        user_prompt = RAW_USER_PROMPT.format(transcript=transcript)

        analysis = await adapter.run_completion_async(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            dto=TranscriptAnalysisDTO,
        )

        store_status = db.store(analysis)

        if store_status.status != DBStatus.SUCCESS:
            raise RuntimeError("Failed to store analysis")

        return TranscriptAnalysisResponse(
            id=store_status.object_id,
            summary=analysis.summary,
            next_actions=analysis.next_actions,
        )

    try:
        results = await asyncio.gather(
            *(process_single_transcript(t) for t in payload.transcripts),
            return_exceptions=False,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    return results
