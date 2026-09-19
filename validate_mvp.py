"""Quick local validation for the GeoAgriSense MVP."""

import importlib.util


packages = [
    ("streamlit", "Streamlit"),
    ("pandas", "Pandas"),
    ("folium", "Folium"),
    ("streamlit_folium", "streamlit-folium"),
    ("dotenv", "python-dotenv"),
    ("google.genai", "google-genai"),
    ("geopandas", "GeoPandas"),
    ("shapely", "Shapely"),
]


print("GeoAgriSense MVP dependency check")
print("-" * 40)

failed = False

for module, label in packages:

    if importlib.util.find_spec(module) is None:
        print(f"FAIL  {label}")
        failed = True
    else:
        print(f"PASS  {label}")


if failed:
    raise SystemExit(
        "\nOne or more required MVP packages are missing."
    )


print()
print("PASS  Core MVP dependencies are installed.")
print()
print("Next:")
print("python -m streamlit run app.py")