"""FastAPI приложение."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from loguru import logger

from src.pipeline.orchestrator import ArchitectureDesignPipeline


app = FastAPI(title="ASUTP-DSS API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"], allow_credentials=True)


class ContextModel(BaseModel):
    team_size: int = 5
    budget_million_rub: float = 10.0
    timeline_months: int = 6
    safety_level_sil: int = 2
    real_time_critical: bool = True
    num_external_systems: int = 3
    has_scada_integration: bool = True
    has_mes_integration: bool = False


class AnalyzeRequest(BaseModel):
    document_text: str = Field(..., min_length=10)
    context: ContextModel
    use_ai: bool = True


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        pipeline = ArchitectureDesignPipeline(use_ai=req.use_ai)
        result = pipeline.run(
            req.document_text, req.context.model_dump(), verbose=False,
        )
        return {
            'requirements_count': len(result.requirements.get('entities', [])),
            'patterns': result.patterns,
            'quality_score': result.quality_assessment.get('overall_score'),
            'timings': result.timings,
            'errors': result.errors,
        }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, str(e))
