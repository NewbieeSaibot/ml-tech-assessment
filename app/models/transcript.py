from pydantic import BaseModel
from typing import List


class TranscriptAnalysisDTO(BaseModel):
    summary: str
    next_actions: List[str]


class TranscriptAnalysisResponse(BaseModel):
    id: str
    summary: str
    next_actions: List[str]


class BatchTranscriptRequest(BaseModel):
    transcripts: List[str]
