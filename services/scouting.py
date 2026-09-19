import pandas as pd


def calculate_risk(row):
    """
    Simple rule-based scouting risk model.

    This is deliberately transparent for the MVP.
    """

    soil = float(row.get("soil_moisture_pct", 50))
    pest = float(row.get("pest_pressure_pct", 0))
    vegetation = float(row.get("vegetation_index", 0.5))

    score = 0

    # Soil moisture stress
    if soil < 40:
        score += 2
    elif soil < 50:
        score += 1

    # Pest pressure
    if pest >= 50:
        score += 3
    elif pest >= 25:
        score += 2
    elif pest >= 10:
        score += 1

    # Vegetation stress
    if vegetation < 0.50:
        score += 3
    elif vegetation < 0.60:
        score += 2
    elif vegetation < 0.70:
        score += 1

    if score >= 5:
        return "High"

    if score >= 2:
        return "Medium"

    return "Low"


def prepare_observations(df):
    """
    Add calculated risk to observation dataframe.
    """

    df = df.copy()

    if "risk" not in df.columns:
        df["risk"] = df.apply(calculate_risk, axis=1)

    return df


def scouting_summary(df):
    """
    Calculate dashboard summary metrics.
    """

    if df.empty:
        return {
            "points": 0,
            "high_risk": 0,
            "avg_moisture": 0,
            "avg_vegetation": 0,
        }

    return {
        "points": len(df),
        "high_risk": int((df["risk"] == "High").sum()),
        "avg_moisture": round(
            float(df["soil_moisture_pct"].mean()), 1
        ),
        "avg_vegetation": round(
            float(df["vegetation_index"].mean()), 2
        ),
    }