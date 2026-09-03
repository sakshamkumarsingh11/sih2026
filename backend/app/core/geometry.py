from app.schemas import SpillGeometry, GeoPoint

def extract_geometry(mask_data: dict, center_lat: float, center_lon: float) -> SpillGeometry:
    """Task 2: Geometry extraction placeholder."""
    return SpillGeometry(
        centroid=GeoPoint(lat=center_lat, lon=center_lon),
        area_km2=14.72,
        perimeter_km=18.4,
        bbox=[center_lat - 0.03, center_lon - 0.03, center_lat + 0.03, center_lon + 0.03],
        orientation_degrees=42.5
    )
