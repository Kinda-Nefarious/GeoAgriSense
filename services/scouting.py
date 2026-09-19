from __future__ import annotations

import pandas as pd


def build_demo_scouting_data() -> pd.DataFrame:
    """
    Synthetic scouting observations for the GeoAgriSense MVP.

    These values are demonstration data only.
    Replace this function later with real sensor, ODK,
    drone, database, or farm scouting data.
    """

    rows = [
        {
            "point_id": "SP-01",
            "crop": "Lettuce",
            "latitude": -17.814,
            "longitude": 31.035,
            "soil_moisture_pct": 72,
            "temperature_c": 24.1,
            "vegetation_index": 0.78,
            "pest_pressure_pct": 8,
        },
        {
            "point_id": "SP-02",
            "crop": "Lettuce",
            "latitude": -17.817,
            "longitude": 31.043,
            "soil_moisture_pct": 54,
            "temperature_c": 26.8,
            "vegetation_index": 0.64,
            "pest_pressure_pct": 24,
        },
        {
            "point_id": "SP-03",
            "crop": "Lettuce",
            "latitude": -17.820,
            "longitude": 31.052,
            "soil_moisture_pct": 31,
            "temperature_c": 29.2,
            "vegetation_index": 0.48,
            "pest_pressure_pct": 58,
        },
        {
            "point_id": "SP-04",
            "crop": "Red cabbage",
            "latitude": -17.823,
            "longitude": 31.061,
            "soil_moisture_pct": 45,
            "temperature_c": 27.6,
            "vegetation_index": 0.59,
            "pest_pressure_pct": 36,
        },
        {
            "point_id": "SP-05",
            "crop": "Red cabbage",
            "latitude": -17.826,
            "longitude": 31.043,
            "soil_moisture_pct": 68,
            "temperature_c": 25.2,
            "vegetation_index": 0.73,
            "pest_pressure_pct": 12,
        },
        {
            "point_id": "SP-06",
            "crop": "Lettuce",
            "latitude": -17.829,
            "longitude": 31.054,
            "soil_moisture_pct": 38,
            "temperature_c": 28.4,
            "vegetation_index": 0.53,
            "pest_pressure_pct": 47,
        },
    ]

    return pd.DataFrame(rows)


def classify_risk(row: pd.Series) -> str:
    """
    Transparent rule-based scouting risk classifier.

    This is deliberately simple for the MVP.
    It is not presented as a trained machine-learning model.
    """

    score = 0

    # Soil moisture
    if row["soil_moisture_pct"] < 40:
        score += 2
    elif row["soil_moisture_pct"] < 55:
        score += 1

    # Temperature
    if row["temperature_c"] > 28:
        score += 1

    # Vegetation condition
    if row["vegetation_index"] < 0.55:
        score += 2
    elif row["vegetation_index"] < 0.65:
        score += 1

    # Pest pressure
    if row["pest_pressure_pct"] > 50:
        score += 2
    elif row["pest_pressure_pct"] > 30:
        score += 1

    if score >= 4:
        return "High"

    if score >= 2:
        return "Medium"

    return "Low"


def summarize_scouting(df: pd.DataFrame) -> dict:
    """Generate dashboard-level scouting indicators."""

    high_risk = int((df["risk"] == "High").sum())

    actions = []

    if (df["soil_moisture_pct"] < 40).any():
        actions.append(
            "Inspect low-moisture zones and verify irrigation performance."
        )

    if (df["pest_pressure_pct"] > 50).any():
        actions.append(
            "Scout high pest-pressure points for visible pest or disease symptoms."
        )

    if (df["vegetation_index"] < 0.55).any():
        actions.append(
            "Inspect low-vegetation areas for water stress, nutrient issues, or crop damage."
        )

    if not actions:
        actions.append(
            "Continue routine scouting and record observations consistently."
        )

    return {
        "high_risk": high_risk,
        "avg_moisture": float(df["soil_moisture_pct"].mean()),
        "avg_vegetation": float(df["vegetation_index"].mean()),
        "actions": actions,
    }