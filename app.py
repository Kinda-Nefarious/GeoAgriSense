import json
import os
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from streamlit_folium import st_folium

from services.gemini_service import ask_gemini
from services.scouting import (
    build_demo_scouting_data,
    classify_risk,
    summarize_scouting,
)


# ============================================================
# Configuration
# ============================================================

load_dotenv()

APP_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="GeoAgriSense",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Styling
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .demo-note {
        padding: 10px 14px;
        border-left: 4px solid #4CAF50;
        background: rgba(76,175,80,.08);
        border-radius: 6px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Header
# ============================================================

st.title("🌱 GeoAgriSense")

st.caption(
    "AI-powered spatial intelligence for smarter farm scouting."
)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.header("GeoAgriSense MVP")

    st.success("Core application loaded")

    st.subheader("Demo controls")

    uploaded_geojson = st.file_uploader(
        "Upload field boundary / GeoJSON",
        type=["geojson", "json"],
        help=(
            "Optional. Upload a real field boundary "
            "to replace the demo geometry."
        ),
    )

    st.divider()

    st.subheader("System status")

    api_key_present = bool(
        os.getenv("GEMINI_API_KEY")
    )

    if api_key_present:
        st.write("Gemini API key: ✅ loaded")
    else:
        st.write("Gemini API key: ❌ missing")

    model_name = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash",
    )

    st.write(f"Gemini model: `{model_name}`")

    st.divider()

    st.caption(
        "Demo measurements are synthetic and are not "
        "measurements from Sunnyside Farm."
    )


# ============================================================
# DATA LAYER
# ============================================================

scout_df = build_demo_scouting_data()

scout_df["risk"] = scout_df.apply(
    classify_risk,
    axis=1,
)

summary = summarize_scouting(
    scout_df
)


# ============================================================
# KPI DASHBOARD
# ============================================================

c1, c2, c3, c4 = st.columns(4)


with c1:
    st.metric(
        "Scouting points",
        len(scout_df),
    )


with c2:
    st.metric(
        "High-risk points",
        summary["high_risk"],
    )


with c3:
    st.metric(
        "Average soil moisture",
        f'{summary["avg_moisture"]:.0f}%',
    )


with c4:
    st.metric(
        "Average vegetation index",
        f'{summary["avg_vegetation"]:.2f}',
    )


st.markdown(
    """
    <div class="demo-note">
        <strong>Demo mode:</strong>
        The scouting measurements shown here are
        synthetic demonstration data.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MAIN TABS
# ============================================================

tab_dashboard, tab_map, tab_scout, tab_ai = st.tabs(
    [
        "📊 Dashboard",
        "🗺️ Spatial Map",
        "🔎 Scout Analysis",
        "🤖 AI Assistant",
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

with tab_dashboard:

    st.subheader("Field overview")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Risk distribution")

        risk_counts = (
            scout_df["risk"]
            .value_counts()
            .reindex(
                ["Low", "Medium", "High"],
                fill_value=0,
            )
        )

        st.bar_chart(risk_counts)


    with col2:

        st.markdown("### Scouting observations")

        display_df = scout_df[
            [
                "point_id",
                "crop",
                "soil_moisture_pct",
                "temperature_c",
                "vegetation_index",
                "pest_pressure_pct",
                "risk",
            ]
        ].copy()

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# SPATIAL MAP
# ============================================================

with tab_map:

    st.subheader("Spatial scouting map")

    # Synthetic demonstration centre.
    demo_center = [
        -17.82,
        31.05,
    ]

    m = folium.Map(
        location=demo_center,
        zoom_start=13,
        control_scale=True,
    )


    # --------------------------------------------------------
    # Demo field boundary
    # --------------------------------------------------------

    folium.Rectangle(
        bounds=[
            [
                demo_center[0] - 0.012,
                demo_center[1] - 0.015,
            ],
            [
                demo_center[0] + 0.012,
                demo_center[1] + 0.015,
            ],
        ],
        color="#2e7d32",
        fill=True,
        fill_opacity=0.08,
        tooltip=(
            "Demo field boundary — "
            "replace with real GeoJSON"
        ),
    ).add_to(m)


    # --------------------------------------------------------
    # Risk colours
    # --------------------------------------------------------

    color_map = {
        "Low": "green",
        "Medium": "orange",
        "High": "red",
    }


    # --------------------------------------------------------
    # Scouting points
    # --------------------------------------------------------

    for _, row in scout_df.iterrows():

        popup_html = f"""
        <b>{row['point_id']}</b><br>
        Crop: {row['crop']}<br>
        Soil moisture:
        {row['soil_moisture_pct']}%<br>
        Temperature:
        {row['temperature_c']} °C<br>
        Vegetation index:
        {row['vegetation_index']}<br>
        Pest pressure:
        {row['pest_pressure_pct']}%<br>
        Risk:
        <b>{row['risk']}</b>
        """

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"],
            ],
            radius=9,
            color=color_map[row["risk"]],
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup(
                popup_html,
                max_width=300,
            ),
        ).add_to(m)


    # --------------------------------------------------------
    # Optional uploaded GeoJSON
    # --------------------------------------------------------

    if uploaded_geojson is not None:

        try:

            geojson_data = json.load(
                uploaded_geojson
            )

            folium.GeoJson(
                geojson_data,
                name="Uploaded field boundary",
                style_function=lambda feature: {
                    "color": "#1565c0",
                    "weight": 3,
                    "fillOpacity": 0.05,
                },
                tooltip="Uploaded field boundary",
            ).add_to(m)

            folium.LayerControl().add_to(m)

            st.success(
                "Uploaded GeoJSON loaded onto the map."
            )

        except Exception as exc:

            st.error(
                f"Could not read GeoJSON: {exc}"
            )


    st_folium(
        m,
        use_container_width=True,
        height=560,
    )


# ============================================================
# SCOUT ANALYSIS
# ============================================================

with tab_scout:

    st.subheader(
        "Scout prioritisation"
    )

    st.write(
        "GeoAgriSense converts field observations "
        "into scouting priorities so farmers can "
        "focus attention where intervention may "
        "be most urgent."
    )


    high_risk = scout_df[
        scout_df["risk"] == "High"
    ]


    if high_risk.empty:

        st.success(
            "No high-risk points in the "
            "current demo dataset."
        )

    else:

        for _, row in high_risk.iterrows():

            st.error(
                f"{row['point_id']} — "
                f"{row['crop']}: prioritise scouting. "
                f"Moisture "
                f"{row['soil_moisture_pct']}%, "
                f"pest pressure "
                f"{row['pest_pressure_pct']}%."
            )


    st.markdown(
        "### Recommended actions"
    )


    for action in summary["actions"]:

        st.write(
            f"• {action}"
        )


# ============================================================
# GEMINI ASSISTANT
# ============================================================

with tab_ai:

    st.subheader(
        "Crop Scouting Assistant"
    )

    st.write(
        "Ask GeoAgriSense an agricultural or "
        "crop-scouting question."
    )


    question = st.text_area(
        "Question",
        value=(
            "Why is regular crop scouting "
            "important for smallholder farmers?"
        ),
        height=120,
    )


    ask = st.button(
        "Ask GeoAgriSense",
        type="primary",
    )


    if ask:

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "GeoAgriSense is consulting Gemini..."
            ):

                result = ask_gemini(
                    question.strip()
                )


            if result["ok"]:

                st.success(
                    "Gemini response"
                )

                st.write(
                    result["text"]
                )

            else:

                st.warning(
                    result["message"]
                )

                if result.get(
                    "technical_detail"
                ):

                    with st.expander(
                        "Technical detail"
                    ):

                        st.code(
                            result[
                                "technical_detail"
                            ]
                        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "GeoAgriSense — Hack for Humanity MVP | "
    "Layered prototype: UI → Data → Spatial → AI"
)