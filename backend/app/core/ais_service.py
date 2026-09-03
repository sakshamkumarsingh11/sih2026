import math
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Dict, Any
from app.schemas import ProbableOrigin, AISCoverageStatus, TrackPoint, GeoPoint


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes the great-circle distance between two coordinates in kilometers."""
    R = 6371.0  # Earth's mean radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c


def generate_synthetic_ais_feed(origin: ProbableOrigin) -> List[Dict[str, Any]]:
    """
    Generates realistic maritime traffic tracks around the incident area
    for demonstration and evaluation when a live commercial AIS feed is unattached.
    """
    mid_time = origin.time_window_start + (origin.time_window_end - origin.time_window_start) / 2
    c_lat, c_lon = origin.centroid.lat, origin.centroid.lon

    return [
        {
            "mmsi": "413219000",
            "vessel_name": "PACIFIC EXPLORER",
            "vessel_type": "Crude Oil Tanker",
            "track": [
                TrackPoint(
                    location=GeoPoint(lat=round(c_lat - 0.012, 5), lon=round(c_lon - 0.010, 5)),
                    timestamp=mid_time - timedelta(minutes=40),
                    sog_knots=13.8,
                    cog_degrees=42.0
                ),
                # Suspicious speed drop near the probable origin
                TrackPoint(
                    location=GeoPoint(lat=round(c_lat + 0.003, 5), lon=round(c_lon + 0.002, 5)),
                    timestamp=mid_time - timedelta(minutes=10),
                    sog_knots=4.5,
                    cog_degrees=40.0
                ),
                TrackPoint(
                    location=GeoPoint(lat=round(c_lat + 0.018, 5), lon=round(c_lon + 0.014, 5)),
                    timestamp=mid_time + timedelta(minutes=25),
                    sog_knots=13.2,
                    cog_degrees=45.0
                )
            ]
        },
        {
            "mmsi": "352001450",
            "vessel_name": "NORDIC STAR",
            "vessel_type": "Container Ship",
            "track": [
                TrackPoint(
                    location=GeoPoint(lat=round(c_lat + 0.05, 5), lon=round(c_lon - 0.03, 5)),
                    timestamp=mid_time - timedelta(minutes=30),
                    sog_knots=18.5,
                    cog_degrees=110.0
                ),
                TrackPoint(
                    location=GeoPoint(lat=round(c_lat + 0.04, 5), lon=round(c_lon + 0.02, 5)),
                    timestamp=mid_time + timedelta(minutes=15),
                    sog_knots=18.2,
                    cog_degrees=112.0
                )
            ]
        },
        {
            "mmsi": "211456000",
            "vessel_name": "ALBATROSS II",
            "vessel_type": "Fishing Vessel",
            "track": [
                TrackPoint(
                    location=GeoPoint(lat=round(c_lat - 0.08, 5), lon=round(c_lon - 0.07, 5)),
                    timestamp=mid_time - timedelta(hours=2),
                    sog_knots=6.0,
                    cog_degrees=270.0
                )
            ]
        }
    ]


def search_nearby_vessels(
    origin: ProbableOrigin,
    external_ais_data: List[Dict[str, Any]] = None
) -> Tuple[AISCoverageStatus, List[Dict[str, Any]]]:
    """
    Task 4: AIS Spatiotemporal Correlator.
    Filters vessels intersecting the origin spatio-temporal envelope.
    """
    # Use synthetic feed if no external AIS records are supplied
    ais_records = external_ais_data if external_ais_data is not None else generate_synthetic_ais_feed(origin)

    if not ais_records:
        return AISCoverageStatus.UNAVAILABLE, []

    candidates = []
    # Search envelope: uncertainty radius with a safety buffer (+5 km)
    search_radius_km = origin.uncertainty_radius_km + 5.0

    for ship in ais_records:
        track = ship.get("track", [])
        if not track:
            continue

        in_spatial_range = False
        in_temporal_range = False

        for pt in track:
            # Check spatial proximity
            dist = haversine_distance_km(
                origin.centroid.lat, origin.centroid.lon,
                pt.location.lat, pt.location.lon
            )
            if dist <= search_radius_km:
                in_spatial_range = True

            # Check temporal window (with 1 hour buffer)
            t_start = origin.time_window_start - timedelta(hours=1)
            t_end = origin.time_window_end + timedelta(hours=1)

            # Ensure datetime comparison works timezone-agnostic
            pt_ts = pt.timestamp.replace(tzinfo=None)
            t_start_clean = t_start.replace(tzinfo=None)
            t_end_clean = t_end.replace(tzinfo=None)

            if t_start_clean <= pt_ts <= t_end_clean:
                in_temporal_range = True

        # Keep vessel if it was in the spatiotemporal neighborhood
        if in_spatial_range and in_temporal_range:
            candidates.append(ship)

    status = AISCoverageStatus.AVAILABLE if len(candidates) > 0 else AISCoverageStatus.PARTIAL
    return status, candidates