from datetime import datetime
from app.schemas import CandidateVessel, ConfidenceLevel, EvidenceBreakdown, TrackPoint, GeoPoint

def rank_vessels(candidates_raw: list, origin_point: GeoPoint) -> list[CandidateVessel]:
    """Task 5: Attribution engine placeholder."""
    return [
        CandidateVessel(
            mmsi="413219000",
            vessel_name="PACIFIC EXPLORER",
            vessel_type="Crude Oil Tanker",
            attribution_score=0.91,
            confidence=ConfidenceLevel.HIGH,
            evidence=EvidenceBreakdown(
                cpa_distance_km=0.8,
                time_discrepancy_min=12.0,
                trajectory_match="STRONG",
                speed_anomaly_detected=True
            ),
            track_history=[
                TrackPoint(
                    location=GeoPoint(lat=origin_point.lat + 0.005, lon=origin_point.lon - 0.004),
                    timestamp=datetime.utcnow(),
                    sog_knots=5.2,
                    cog_degrees=215.0
                )
            ]
        )
    ]
