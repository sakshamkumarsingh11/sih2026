from fastapi import APIRouter, UploadFile, File, Form
from datetime import datetime
from app.schemas import SpillAnalysisResponse
from app.core.segmentation import run_segmentation
from app.core.geometry import extract_geometry
from app.core.drift_engine import compute_drift
from app.core.ais_service import search_nearby_vessels
from app.core.attribution import rank_vessels

router = APIRouter()

@router.post("/analyze", response_model=SpillAnalysisResponse, summary="Analyze SAR image and attribute spill")
async def analyze_spill(
    file: UploadFile = File(..., description="Sentinel-1 SAR image (GeoTIFF/PNG)"),
    approx_lat: float = Form(15.2105, description="Approximate observation Latitude"),
    approx_lon: float = Form(65.4210, description="Approximate observation Longitude"),
    observation_time: datetime = Form(default_factory=datetime.utcnow)
):
    image_bytes = await file.read()

    seg_result = run_segmentation(image_bytes)
    geom = extract_geometry(seg_result, approx_lat, approx_lon)
    drift = compute_drift(geom.centroid, observation_time)
    ais_status, candidates_raw = search_nearby_vessels(drift.hindcast_origin)
    ranked_vessels = rank_vessels(candidates_raw, drift.hindcast_origin.centroid)

    return SpillAnalysisResponse(
        spill_id="SPILL_2026_001",
        detection_timestamp=observation_time,
        segmentation_confidence=seg_result["confidence"],
        geometry=geom,
        drift=drift,
        ais_status=ais_status,
        ranked_vessels=ranked_vessels,
        status_message="Analysis completed successfully."
    )
