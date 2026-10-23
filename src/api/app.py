"""FastAPI приложение для СППР АСУ ТП."""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from loguru import logger
import tempfile
from pathlib import Path

from src.pipeline.orchestrator import ArchitectureDesignPipeline


app = FastAPI(
    title="ASUTP-DSS API",
    description="СППР для проектирования архитектуры ПО АСУ ТП",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class PatternResult(BaseModel):
    pattern: str
    confidence: float


class AnalyzeResponse(BaseModel):
    requirements_count: int
    patterns: List[PatternResult]
    quality_score: Optional[float]
    timings: Dict[str, float]
    errors: List[str]


@app.get("/")
def root():
    return {"name": "ASUTP-DSS API", "version": "0.1.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(req: AnalyzeRequest):
    """Анализ текста ТЗ."""
    try:
        pipeline = ArchitectureDesignPipeline(use_ai=req.use_ai)
        result = pipeline.run(
            req.document_text,
            req.context.model_dump(),
            verbose=False,
        )
        
        return AnalyzeResponse(
            requirements_count=len(result.requirements.get('entities', [])),
            patterns=[
                PatternResult(pattern=p['pattern'], confidence=p['confidence'])
                for p in result.patterns
            ],
            quality_score=result.quality_assessment.get('overall_score'),
            timings=result.timings,
            errors=result.errors,
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...), use_ai: bool = True):
    """Анализ загруженного файла."""
    content = await file.read()
    
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(400, "Файл должен быть UTF-8")
    
    try:
        pipeline = ArchitectureDesignPipeline(use_ai=use_ai)
        result = pipeline.run(
            text,
            {
                'team_size': 5,
                'budget_million_rub': 10.0,
                'timeline_months': 6,
                'safety_level_sil': 2,
                'real_time_critical': True,
                'num_external_systems': 3,
                'has_scada_integration': True,
                'has_mes_integration': False,
            },
            verbose=False,
        )
        
        return {
            'requirements_count': len(result.requirements.get('entities', [])),
            'patterns': result.patterns,
            'quality_score': result.quality_assessment.get('overall_score'),
            'timings': result.timings,
        }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, str(e))