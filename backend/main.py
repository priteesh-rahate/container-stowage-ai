

import io
import pandas as pd

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.voyage_simulation import simulate_voyage
from backend.vessel_layout import create_vessel_layout
from backend.ai_service import ask_local_ai
from backend.models import CargoManifest
from backend.slots import VesselSlotPlan
from backend.placement import create_stowage_plan



app = FastAPI(
    title="AI-Driven Container Vessel Cargo Scheduling and Voyage Planning System",
    description="Local AI-assisted container stowage and voyage planning.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlanningRequest(BaseModel):
    manifest: CargoManifest
    vessel: VesselSlotPlan | None = None

class VoyageSimulationRequest(BaseModel):
    manifest: CargoManifest
    port_sequence: list[str] = Field(min_length=2)
    vessel: VesselSlotPlan | None = None

@app.get("/")
def home():
    return {
        "message": "Container Stowage API is running",
        "status": "ok",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "container-stowage-api",
        "ai_runtime": "Ollama",
    }


@app.post("/api/plan")
def generate_plan(request: PlanningRequest):
    if not request.manifest.containers:
        raise HTTPException(
            status_code=400,
            detail="Cargo manifest cannot be empty.",
        )

    try:
        vessel = request.vessel or create_vessel_layout()

        return create_stowage_plan(
            request.manifest,
            vessel,
        )        
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

from pydantic import BaseModel, Field


class AIQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@app.post("/api/ai/ask")
def ask_ai(request: AIQuestion):
    try:
        answer = ask_local_ai(request.question)
        return {
            "model": "qwen2.5:7b",
            "answer": answer,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Local AI service unavailable: {exc}",
        ) from exc


@app.post("/api/manifest/upload")
async def upload_manifest(file: UploadFile = File(...)):
    filename = (file.filename or "").lower()

    try:
        content = await file.read()

        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        else:
            raise HTTPException(
                status_code=400,
                detail="Upload a CSV (.csv) or Excel (.xlsx) file.",
            )

        required_columns = [
            "container_id",
            "size_ft",
            "weight_kg",
            "loading_port",
            "discharge_port",
        ]

        missing = [
            column for column in required_columns
            if column not in df.columns
        ]

        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing)}",
            )

        df = df.where(pd.notna(df), None)       

        return {
            "filename": file.filename,
            "total_rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(10).to_dict(orient="records"),
            "containers": df.to_dict(orient="records"),
            "message": "File uploaded and required columns checked.",
        }


    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read the uploaded file: {exc}",
        )
    finally:
        await file.close()

@app.post("/api/voyage/simulate")
def simulate_voyage_endpoint(request: VoyageSimulationRequest):
    vessel = request.vessel or create_vessel_layout()

    return simulate_voyage(
        manifest=request.manifest,
        vessel=vessel,
        port_sequence=request.port_sequence,
    )


@app.get("/api/vessel/layout")
def get_vessel_layout():
    vessel = create_vessel_layout()
    return vessel.model_dump()

