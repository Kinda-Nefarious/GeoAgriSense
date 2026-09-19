import pandas as pd


SEVERITY_ORDER = {
    "High": 4,
    "Investigate": 3,
    "Watch": 2,
    "Low": 1,
}


def normalize_severity(value):
    """Normalize different severity labels into dashboard categories."""
    if value is None:
        return "Watch"

    value = str(value).strip().lower()

    mapping = {
        "high": "High",
        "severe": "High",
        "critical": "High",
        "investigate": "Investigate",
        "medium": "Investigate",
        "moderate": "Investigate",
        "watch": "Watch",
        "low": "Low",
        "minor": "Low",
    }

    return mapping.get(value, "Watch")


def calculate_risk(row):
    """
    Calculate risk from environmental/scouting measurements.

    Used primarily for sample_scouting.csv.
    Actual GeoJSON observations retain their supplied severity.
    """

    soil = float(row.get("soil_moisture_pct", 50))
    pest = float(row.get("pest_pressure_pct", 0))
    vegetation = float(row.get("vegetation_index", 0.5))

    score = 0

    if soil < 40:
        score += 2
    elif soil < 50:
        score += 1

    if pest >= 50:
        score += 3
    elif pest >= 25:
        score += 2
    elif pest >= 10:
        score += 1

    if vegetation < 0.50:
        score += 3
    elif vegetation < 0.60:
        score += 2
    elif vegetation < 0.70:
        score += 1

    if score >= 5:
        return "High"

    if score >= 2:
        return "Investigate"

    return "Low"


def prepare_observations(df):
    """
    Prepare CSV scouting data.

    Existing GeoJSON observations with a supplied severity are not
    overwritten.
    """

    df = df.copy()

    if "severity" in df.columns:
        df["severity"] = df["severity"].apply(normalize_severity)

    if "risk" not in df.columns:
        if {
            "soil_moisture_pct",
            "pest_pressure_pct",
            "vegetation_index",
        }.issubset(df.columns):
            df["risk"] = df.apply(calculate_risk, axis=1)
        else:
            df["risk"] = (
                df["severity"]
                if "severity" in df.columns
                else "Watch"
            )

    return df


def observation_summary(df):
    """Return dashboard summary statistics for GeoJSON observations."""

    if df.empty:
        return {
            "total": 0,
            "high": 0,
            "investigate": 0,
            "watch": 0,
            "low": 0,
        }

    severity = (
        df["severity"]
        .fillna("Watch")
        .apply(normalize_severity)
    )

    return {
        "total": len(df),
        "high": int((severity == "High").sum()),
        "investigate": int(
            (severity == "Investigate").sum()
        ),
        "watch": int((severity == "Watch").sum()),
        "low": int((severity == "Low").sum()),
    }


def scouting_summary(df):
    """Summary for environmental scouting CSV."""

    if df.empty:
        return {
            "points": 0,
            "high_risk": 0,
            "avg_moisture": 0,
            "avg_vegetation": 0,
        }

    risk_column = (
        df["risk"]
        if "risk" in df.columns
        else pd.Series(["Low"] * len(df))
    )

    return {
        "points": len(df),
        "high_risk": int(
            (risk_column == "High").sum()
        ),
        "avg_moisture": (
            round(float(df["soil_moisture_pct"].mean()), 1)
            if "soil_moisture_pct" in df.columns
            else 0
        ),
        "avg_vegetation": (
            round(float(df["vegetation_index"].mean()), 2)
            if "vegetation_index" in df.columns
            else 0
        ),
    }