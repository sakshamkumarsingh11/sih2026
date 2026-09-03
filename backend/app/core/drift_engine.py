from datetime import datetime, timedelta
from app.schemas import SpillDrift, ProbableOrigin, DriftPoint, GeoPoint

def compute_drift(centroid: GeoPoint, detection_time: datetime) -> SpillDrift:
    """Task 3: Drift calculation placeholder."""
    origin = ProbableOrigin(
        centroid=GeoPoint(lat=centroid.lat - 0.09, lon=centroid.lon - 0.11),
        time_window_start=detection_time - timedelta(hours=6),
        time_window_end=detection_time - timedelta(hours=4),
        uncertainty_radius_km=3.5
    )
    forecast = [
        DriftPoint(timestamp=detection_time + timedelta(hours=6), location=GeoPoint(lat=centroid.lat + 0.07, lon=centroid.lon + 0.08)),
        DriftPoint(timestamp=detection_time + timedelta(hours=12), location=GeoPoint(lat=centroid.lat + 0.14, lon=centroid.lon + 0.16))
    ]
    return SpillDrift(hindcast_origin=origin, forecast_trajectory=forecast)
