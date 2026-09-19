import json
from pathlib import Path

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

from services.gemini_service import GeminiService
from services.scouting import (
    prepare_observations,
    observation_summary,
    scouting_summary,
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

OBSERVATIONS_FILE = DATA_DIR / "observations.geojson"
BLOCKS_FILE = DATA_DIR / "blocks.geojson"
BOUNDARY_FILE = DATA_DIR / "farm_boundary.geojson"
SCOUTING_FILE = DATA_DIR / "sample_scouting.csv"


st.set_page_config(
    page_title="GeoAgriSense",
    page_icon="🌱",
    layout="wide",
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_geojson(path):

    if not path.exists():
        return None

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


@st.cache_data
def load_observations(path):

    data = load_geojson(path)

    if not data:
        return pd.DataFrame()

    rows = []

    for feature in data.get(
        "features",
        [],
    ):

        properties = (
            feature.get(
                "properties",
                {},
            )
            .copy()
        )

        geometry = feature.get(
            "geometry",
            {},
        )

        coordinates = geometry.get(
            "coordinates",
            [None, None],
        )

        properties["longitude"] = coordinates[0]
        properties["latitude"] = coordinates[1]

        rows.append(properties)

    if not rows:
        return pd.DataFrame()

    return prepare_observations(
        pd.DataFrame(rows)
    )


@st.cache_data
def load_blocks(path):

    data = load_geojson(path)

    if not data:
        return pd.DataFrame()

    rows = []

    for feature in data.get(
        "features",
        [],
    ):

        properties = (
            feature.get(
                "properties",
                {},
            )
            .copy()
        )

        properties["geometry"] = feature.get(
            "geometry"
        )

        rows.append(properties)

    return pd.DataFrame(rows)


@st.cache_data
def load_scouting(path):

    if not path.exists():
        return pd.DataFrame()

    try:

        return prepare_observations(
            pd.read_csv(path)
        )

    except Exception:

        return pd.DataFrame()


@st.cache_resource
def get_gemini():

    try:
        return GeminiService()

    except Exception:
        return None


# ============================================================
# LOAD DATA
# ============================================================

observations = load_observations(
    OBSERVATIONS_FILE
)

blocks = load_blocks(
    BLOCKS_FILE
)

boundary = load_geojson(
    BOUNDARY_FILE
)

scouting = load_scouting(
    SCOUTING_FILE
)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🌱 GeoAgriSense")

st.subheader(
    "AI-powered spatial intelligence for smarter farm scouting"
)

st.caption(
    "Combining field observations, geospatial context and "
    "Gemini multimodal AI to help farmers prioritise action."
)


# ============================================================
# SYSTEM STATUS
# ============================================================

gemini = get_gemini()

with st.sidebar:

    st.header("System")

    if gemini:

        st.success(
            "Gemini API connected"
        )

        st.caption(
            f"Model: `{gemini.model}`"
        )

    else:

        st.error(
            "Gemini API unavailable"
        )

    st.divider()

    st.header("Data layers")

    st.write(
        f"🗺️ Farm boundary: "
        f"{'Loaded' if boundary else 'Missing'}"
    )

    st.write(
        f"🌱 Production blocks: "
        f"{len(blocks)}"
    )

    st.write(
        f"📍 Field observations: "
        f"{len(observations)}"
    )

    st.write(
        f"📊 Scouting measurements: "
        f"{len(scouting)}"
    )

    st.divider()

    st.caption(
        "The supplied field dataset is demonstration data. "
        "It should not be represented as live farm telemetry."
    )


# ============================================================
# KPI DASHBOARD
# ============================================================

obs_summary = observation_summary(
    observations
)

block_count = len(blocks)

most_affected_block = "—"

if not observations.empty and "block_id" in observations:

    counts = observations[
        "block_id"
    ].value_counts()

    if not counts.empty:

        most_affected_block = (
            counts.index[0]
        )


col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.metric(
        "Farm blocks",
        block_count,
    )

with col2:

    st.metric(
        "Observations",
        obs_summary["total"],
    )

with col3:

    st.metric(
        "High severity",
        obs_summary["high"],
    )

with col4:

    st.metric(
        "Investigate",
        obs_summary["investigate"],
    )

with col5:

    st.metric(
        "Most observed block",
        most_affected_block,
    )


st.divider()


# ============================================================
# TABS
# ============================================================

(
    dashboard_tab,
    map_tab,
    observations_tab,
    ai_tab,
    image_tab,
) = st.tabs(
    [
        "📊 Dashboard",
        "🗺️ Spatial Intelligence",
        "📍 Field Observations",
        "🤖 AI Assistant",
        "📷 Gemini Crop Analysis",
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

with dashboard_tab:

    st.header(
        "Farm intelligence overview"
    )

    left, right = st.columns(2)

    with left:

        st.subheader(
            "Observation severity"
        )

        severity_chart = pd.DataFrame(
            {
                "Observations": [
                    obs_summary["high"],
                    obs_summary["investigate"],
                    obs_summary["watch"],
                    obs_summary["low"],
                ]
            },
            index=[
                "High",
                "Investigate",
                "Watch",
                "Low",
            ],
        )

        st.bar_chart(
            severity_chart
        )

    with right:

        st.subheader(
            "Observations by block"
        )

        if (
            not observations.empty
            and "block_id" in observations
        ):

            block_counts = (
                observations[
                    "block_id"
                ]
                .value_counts()
            )

            st.bar_chart(
                block_counts
            )

        else:

            st.info(
                "No block identifiers available."
            )

    st.subheader(
        "Recent field observations"
    )

    if not observations.empty:

        display_columns = [
            "observation_id",
            "block_id",
            "crop",
            "symptom",
            "severity",
            "notes",
        ]

        available = [
            column
            for column in display_columns
            if column in observations.columns
        ]

        st.dataframe(
            observations[available],
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.warning(
            "No observation data found."
        )


# ============================================================
# SPATIAL MAP
# ============================================================

with map_tab:

    st.header(
        "🗺️ Spatial field intelligence"
    )

    st.write(
        "GeoAgriSense combines farm boundaries, production "
        "blocks and georeferenced observations in one view."
    )

    if observations.empty:

        st.warning(
            "No georeferenced observations are available."
        )

    else:

        center = [
            observations["latitude"].mean(),
            observations["longitude"].mean(),
        ]

        fmap = folium.Map(
            location=center,
            zoom_start=16,
            control_scale=True,
        )

        # ----------------------------------------------------
        # FARM BOUNDARY
        # ----------------------------------------------------

        if boundary:

            folium.GeoJson(
                boundary,
                name="Farm boundary",
                style_function=lambda feature: {
                    "fillColor": "#2e7d32",
                    "color": "#1b5e20",
                    "weight": 2,
                    "fillOpacity": 0.08,
                },
                tooltip="Farm boundary",
            ).add_to(fmap)

        # ----------------------------------------------------
        # PRODUCTION BLOCKS
        # ----------------------------------------------------

        if not blocks.empty:

            block_features = []

            for _, block in blocks.iterrows():

                geometry = block.get(
                    "geometry"
                )

                if not geometry:
                    continue

                block_id = block.get(
                    "block_id",
                    block.get(
                        "id",
                        "Block",
                    ),
                )

                crop = block.get(
                    "crop",
                    "Unknown",
                )

                area = block.get(
                    "area_ha",
                    block.get(
                        "area",
                        "Unknown",
                    ),
                )

                popup = (
                    f"<b>Block:</b> {block_id}<br>"
                    f"<b>Crop:</b> {crop}<br>"
                    f"<b>Area:</b> {area} ha"
                )

                folium.GeoJson(
                    geometry,
                    name=f"Block {block_id}",
                    style_function=lambda feature: {
                        "fillColor": "#66bb6a",
                        "color": "#388e3c",
                        "weight": 1.5,
                        "fillOpacity": 0.15,
                    },
                    popup=folium.Popup(
                        popup,
                        max_width=300,
                    ),
                    tooltip=f"{block_id} — {crop}",
                ).add_to(fmap)

        # ----------------------------------------------------
        # OBSERVATIONS
        # ----------------------------------------------------

        for _, row in observations.iterrows():

            severity = str(
                row.get(
                    "severity",
                    "Watch",
                )
            )

            colour = {
                "High": "red",
                "Investigate": "orange",
                "Watch": "blue",
                "Low": "green",
            }.get(
                severity,
                "gray",
            )

            observation_id = row.get(
                "observation_id",
                row.get(
                    "id",
                    "Observation",
                ),
            )

            block_id = row.get(
                "block_id",
                "Unknown",
            )

            crop = row.get(
                "crop",
                "Unknown",
            )

            symptom = row.get(
                "symptom",
                row.get(
                    "observation",
                    "Unknown",
                ),
            )

            notes = row.get(
                "notes",
                "",
            )

            popup = f"""
            <b>{observation_id}</b><br>
            <b>Block:</b> {block_id}<br>
            <b>Crop:</b> {crop}<br>
            <b>Observation:</b> {symptom}<br>
            <b>Severity:</b> {severity}<br>
            <b>Notes:</b> {notes}
            """

            folium.Marker(
                location=[
                    row["latitude"],
                    row["longitude"],
                ],
                popup=folium.Popup(
                    popup,
                    max_width=350,
                ),
                tooltip=(
                    f"{observation_id} — "
                    f"{severity}"
                ),
                icon=folium.Icon(
                    color=colour,
                    icon="leaf",
                    prefix="fa",
                ),
            ).add_to(fmap)

        folium.LayerControl().add_to(
            fmap
        )

        st_folium(
            fmap,
            width=None,
            height=650,
            returned_objects=[],
        )


# ============================================================
# FIELD OBSERVATIONS
# ============================================================

with observations_tab:

    st.header(
        "📍 Field observation explorer"
    )

    if observations.empty:

        st.warning(
            "No observations available."
        )

    else:

        if "observation_id" in observations.columns:

            ids = observations[
                "observation_id"
            ].astype(str).tolist()

        else:

            ids = observations.index.astype(
                str
            ).tolist()

        selected_id = st.selectbox(
            "Select an observation",
            ids,
        )

        if "observation_id" in observations.columns:

            selected = observations[
                observations[
                    "observation_id"
                ].astype(str)
                == selected_id
            ].iloc[0]

        else:

            selected = observations.loc[
                int(selected_id)
            ]

        st.subheader(
            f"{selected_id}"
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Block",
                selected.get(
                    "block_id",
                    "—",
                ),
            )

        with c2:
            st.metric(
                "Crop",
                selected.get(
                    "crop",
                    "—",
                ),
            )

        with c3:
            st.metric(
                "Symptom",
                selected.get(
                    "symptom",
                    selected.get(
                        "observation",
                        "—",
                    ),
                ),
            )

        with c4:
            st.metric(
                "Severity",
                selected.get(
                    "severity",
                    "—",
                ),
            )

        st.write(
            "**Scout notes:**",
            selected.get(
                "notes",
                "No notes supplied.",
            ),
        )

        st.write(
            "**Location:**",
            f"{selected.get('latitude', '—')}, "
            f"{selected.get('longitude', '—')}",
        )

        st.divider()

        st.subheader(
            "AI-assisted assessment"
        )

        st.info(
            "Select this observation and upload its "
            "photograph in the Gemini Crop Analysis tab "
            "to combine field context with multimodal AI."
        )


# ============================================================
# AI ASSISTANT
# ============================================================

with ai_tab:

    st.header(
        "🤖 GeoAgriSense AI Assistant"
    )

    question = st.text_area(
        "Ask an agricultural scouting question",
        value=(
            "What should a farmer check when lettuce "
            "shows wilting despite recent irrigation?"
        ),
        height=120,
    )

    if st.button(
        "Ask Gemini",
        type="primary",
        key="ask_gemini",
    ):

        if not gemini:

            st.error(
                "Gemini is not configured."
            )

        elif not question.strip():

            st.warning(
                "Enter a question first."
            )

        else:

            with st.spinner(
                "Gemini is analysing..."
            ):

                answer = gemini.ask(
                    question.strip()
                )

            st.markdown(
                answer
            )


# ============================================================
# GEMINI IMAGE ANALYSIS
# ============================================================

with image_tab:

    st.header(
        "📷 Multimodal Crop Analysis"
    )

    st.write(
        "Upload a field photograph. GeoAgriSense combines "
        "the photograph with structured field observation "
        "context before sending it to Gemini."
    )

    if observations.empty:

        st.warning(
            "No field observations are available."
        )

    else:

        ids = (
            observations[
                "observation_id"
            ]
            .astype(str)
            .tolist()
            if "observation_id"
            in observations.columns
            else observations.index.astype(
                str
            ).tolist()
        )

        selected_image_observation = st.selectbox(
            "Observation context",
            ids,
            key="image_observation",
        )

        if "observation_id" in observations.columns:

            selected_obs = observations[
                observations[
                    "observation_id"
                ].astype(str)
                == selected_image_observation
            ].iloc[0]

        else:

            selected_obs = observations.loc[
                int(selected_image_observation)
            ]

        st.info(
            f"Gemini context: "
            f"{selected_obs.get('block_id', 'Unknown')} · "
            f"{selected_obs.get('crop', 'Unknown')} · "
            f"{selected_obs.get('severity', 'Unknown')}"
        )

        uploaded_image = st.file_uploader(
            "Upload crop photograph",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp",
            ],
            key="gemini_crop_image",
        )

        if uploaded_image:

            st.image(
                uploaded_image,
                caption="Field photograph",
                use_container_width=True,
            )

        if st.button(
            "🔬 Analyse Observation with Gemini",
            type="primary",
            key="analyse_observation",
        ):

            if not uploaded_image:

                st.warning(
                    "Upload a crop photograph first."
                )

            elif not gemini:

                st.error(
                    "Gemini is not available."
                )

            else:

                observation_context = (
                    selected_obs.to_dict()
                )

                with st.spinner(
                    "Gemini is analysing the photograph "
                    "and field context..."
                ):

                    result = (
                        gemini.analyze_observation(
                            image_bytes=(
                                uploaded_image.getvalue()
                            ),
                            mime_type=(
                                uploaded_image.type
                            ),
                            observation=(
                                observation_context
                            ),
                        )
                    )

                st.subheader(
                    "Gemini Scouting Report"
                )

                st.markdown(
                    result
                )

                st.caption(
                    "AI-generated decision support. "
                    "A field scout or agricultural specialist "
                    "should confirm important findings before "
                    "treatment decisions."
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "GeoAgriSense MVP · Hack for Humanity Harare 2026 · "
    "Spatial Intelligence + Multimodal Gemini AI"
)