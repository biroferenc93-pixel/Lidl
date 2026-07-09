import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(layout="wide")
st.title("🗺️ Üzlethálózat + GDP térkép")

# ---- DATA ----
df = pd.read_excel("Lidl_üzletek.xlsx")

stores = {
    "Lidl": "Lidl üzletek száma",
    "Aldi": "Aldi üzletek száma",
    "Penny": "Penny üzletek száma",
    "Tesco": "Tesco üzletek száma",  # ← EZ HIÁNYZOTT
    "Auchan": "Auchan üzletek száma",
    "Spar": "Spar üzletek száma"
}

colors = {
    "Lidl": "#0050FF",     # erős kék
    "Aldi": "#00A651",     # zöld
    "Penny": "#FF8C00",    # narancs
    "Tesco": "#E60023",    # 🔴 ERŐS PIROS (jól látható!)
    "Auchan": "#6A0DAD",   # lila
    "Spar": "#007A33"   # 🟢 sötét Spar-zöld (nagyon jól látszik)
}

store_list = list(stores.keys())

# ---- GDP (PONTOS NEVEKKEL) ----
gdp_df = pd.DataFrame([
    ["Budapest", 220.8],
    ["Pest", 84.1],
    ["Fejér", 87.7],
    ["Komárom-Esztergom", 95.5],
    ["Veszprém", 75.9],
    ["Győr-Moson-Sopron", 101.1],
    ["Vas", 79.7],
    ["Zala", 67.8],
    ["Baranya", 67.1],
    ["Somogy", 60.0],
    ["Tolna", 71.5],
    ["Borsod-Abaúj-Zemplén", 62.7],
    ["Heves", 71.0],
    ["Nógrád", 45.7],
    ["Hajdú-Bihar", 74.4],
    ["Jász-Nagykun-Szolnok", 63.6],
    ["Szabolcs-Szatmár-Bereg", 57.9],
    ["Bács-Kiskun", 73.4],
    ["Békés", 57.2],
    ["Csongrád", 72.5]  # ⚠️ itt figyelj!
], columns=["megye", "gdp"])

# ---- GÉPJÁRMŰ ADATOK (2025) ----
cars_df = pd.DataFrame([
    ["Budapest", 731370],
    ["Pest", 686979],
    ["Fejér", 204575],
    ["Komárom-Esztergom", 141725],
    ["Veszprém", 164623],
    ["Győr-Moson-Sopron", 240967],
    ["Vas", 128747],
    ["Zala", 133485],
    ["Baranya", 156021],
    ["Somogy", 141511],
    ["Tolna", 97058],
    ["Borsod-Abaúj-Zemplén", 236390],
    ["Heves", 125030],
    ["Nógrád", 79062],
    ["Hajdú-Bihar", 210330],
    ["Jász-Nagykun-Szolnok", 142799],
    ["Szabolcs-Szatmár-Bereg", 211906],
    ["Bács-Kiskun", 243378],
    ["Békés", 131494],
    ["Csongrád", 166843]
], columns=["megye", "cars"])

# ---- LAKOSSÁG (2025) ----
pop_df = pd.DataFrame([
    ["Budapest", 1685209],
    ["Pest", 1336134],
    ["Fejér", 418562],
    ["Komárom-Esztergom", 299262],
    ["Veszprém", 333345],
    ["Győr-Moson-Sopron", 471648],
    ["Vas", 245598],
    ["Zala", 257371],
    ["Baranya", 351158],
    ["Somogy", 290245],
    ["Tolna", 204567],
    ["Borsod-Abaúj-Zemplén", 610927],
    ["Heves", 282490],
    ["Nógrád", 178815],
    ["Hajdú-Bihar", 520129],
    ["Jász-Nagykun-Szolnok", 349726],
    ["Szabolcs-Szatmár-Bereg", 520551],
    ["Bács-Kiskun", 488547],
    ["Békés", 307112],
    ["Csongrád", 388106]
], columns=["megye", "population"])

# ---- LIDL DB / MEGYE ----
lidl_per_county = df.groupby("megye")["Lidl üzletek száma"].sum().reset_index()
lidl_per_county.columns = ["megye", "lidl_count"]

# ---- MERGE + MUTATÓ ----
lidl_analysis = lidl_per_county.merge(pop_df, on="megye")

lidl_analysis["lidl_per_100k"] = (
    lidl_analysis["lidl_count"] / lidl_analysis["population"] * 100000
)

# ---- GEOJSON ----
with open("counties.geojson", encoding="utf-8") as f:
    geo = json.load(f)

# ---- SIDEBAR ----
st.sidebar.header("Beállítások")

selected = st.sidebar.multiselect(
    "Boltláncok",
    store_list,
    default=store_list
)

show_labels = st.sidebar.checkbox("Városnevek mutatása", value=False)
show_gdp = st.sidebar.checkbox("GDP réteg", value=True)
show_cars = st.sidebar.checkbox("Gépjárművek száma réteg", value=False)
show_pop = st.sidebar.checkbox("Lakosság réteg", value=False)
show_lidl_density = st.sidebar.checkbox("Lidl / 100k lakos", value=False)

# ---- LEGEND ----
st.sidebar.markdown("### Boltláncok")
for s in store_list:
    st.sidebar.markdown(
        f"<span style='color:{colors[s]}; font-weight:bold'>●</span> {s}",
        unsafe_allow_html=True
    )

# ---- MAP ----
m = folium.Map(
    location=[47.2, 19.3],
    zoom_start=7,
    tiles="cartodbpositron"
)

m.get_root().header.add_child(folium.Element("""
<style>
.leaflet-control-container .legend {
    display:none !important;
}
</style>
"""))

# ---- GDP CHOROPLETH (EZ A LÉNYEG) ----
if show_gdp:
    folium.Choropleth(
        geo_data=geo,
        data=gdp_df,
        columns=["megye", "gdp"],
        key_on="feature.properties.megye",
        bins=[0, 60, 70, 80, 100, 250],
        fill_color="YlOrRd",
        fill_opacity=0.6,
        line_opacity=0.4,
        ).add_to(m)

# ---- GÉPJÁRMŰ CHOROPLETH ----
if show_cars:
    folium.Choropleth(
        geo_data=geo,
        data=cars_df,
        columns=["megye", "cars"],
        key_on="feature.properties.megye",
        bins=[0, 100000, 150000, 200000, 300000, 800000],
        fill_color="PuBuGn",
        fill_opacity=0.6,
        line_opacity=0.4,
        legend_name="Gépjárművek száma (2025)"
    ).add_to(m)

# ---- LAKOSSÁG CHOROPLETH ----
if show_pop:
    folium.Choropleth(
        geo_data=geo,
        data=pop_df,
        columns=["megye", "population"],
        key_on="feature.properties.megye",
        bins=[0, 200000, 300000, 400000, 600000, 1700000],
        fill_color="PuRd",
        fill_opacity=0.6,
        line_opacity=0.4,
        legend_name="Lakosság (2025)"
    ).add_to(m)

# ---- LIDL SŰRŰSÉG ----
if show_lidl_density:
    folium.Choropleth(
        geo_data=geo,
        data=lidl_analysis,
        columns=["megye", "lidl_per_100k"],
        key_on="feature.properties.megye",
        bins=[0, 2, 4, 6, 8, 15],
        fill_color="YlGnBu",
        fill_opacity=0.7,
        line_opacity=0.4,
        legend_name="Lidl üzletek / 100 000 lakos"
    ).add_to(m)

# ---- MEGYE HATÁR ----
folium.GeoJson(
    geo,
    style_function=lambda x: {
        "fillOpacity": 0,
        "color": "black",
        "weight": 1
    }
).add_to(m)

# ---- OFFSET ----
offsets = [
    (0.006, 0),
    (0, 0.006),
    (-0.006, 0),
    (0, -0.006),
    (0.004, 0.004),
    (-0.004, -0.004)
]

# ---- PONTOK ----
for _, row in df.iterrows():

    present = [
        i for i, s in enumerate(store_list)
        if s in selected and row[stores[s]] > 0
    ]

    if not present:
        continue

    folium.CircleMarker(
        location=[row["lat"], row["lng"]],
        radius=5,
        color="white",
        weight=1,
        fill=True,
        fill_color="#eeeeee",
        fill_opacity=1
    ).add_to(m)

    for idx in present:
        store = store_list[idx]

        scale = 1.5 if row["Város"] == "Budapest" else 1

        lat_off = row["lat"] + offsets[idx][0] * scale
        lon_off = row["lng"] + offsets[idx][1] * scale

        folium.CircleMarker(
            location=[lat_off, lon_off],
            radius=3,
            color="white",
            weight=0.7,
            fill=True,
            fill_color=colors[store],
            fill_opacity=1
        ).add_to(m)

    if show_labels:
        folium.Marker(
            location=[row["lat"], row["lng"]],
            icon=folium.DivIcon(
                html=f"<div style='font-size:10px'>{row['Város']}</div>"
            )
        ).add_to(m)

# ---- GDP LEGEND ----
if show_gdp:
    legend_gdp = """
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        width: 260px;
        background-color: white;
        border-radius: 10px;
        padding: 12px;
        box-shadow: 0 0 12px rgba(0,0,0,0.25);
        font-size: 14px;
        z-index:9999;
    ">
    <b>GDP per capita<br>(% of national average)</b><br><br>

    <span style="background:#ffffcc; padding:4px 10px;"></span> 45–60% (very weak)<br>
    <span style="background:#ffeda0; padding:4px 10px;"></span> 60–70% (weak)<br>
    <span style="background:#feb24c; padding:4px 10px;"></span> 70–80% (average)<br>
    <span style="background:#fc4e2a; padding:4px 10px;"></span> 80–100% (strong)<br>
    <span style="background:#b10026; padding:4px 10px;"></span> 100%+ (outstanding)

    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_gdp))


# ---- GÉPJÁRMŰ LEGEND ----
if show_cars:
    legend_cars = """
    <div style="
        position: fixed; 
        bottom: 50px;
        left: 50px;
        width: 260px;
        background-color: white;
        border-radius: 10px;
        padding: 12px;
        box-shadow: 0 0 12px rgba(0,0,0,0.25);
        font-size: 14px;
        z-index:9999;
    ">
    <b>Közúti gépjárművek száma<br>(2025)</b><br><br>

    <span style="background:#edf8fb; padding:4px 10px;"></span> 0 – 100 000 (nagyon alacsony)<br>
    <span style="background:#b2e2e2; padding:4px 10px;"></span> 100k – 150k (alacsony)<br>
    <span style="background:#66c2a4; padding:4px 10px;"></span> 150k – 200k (közepes)<br>
    <span style="background:#2ca25f; padding:4px 10px;"></span> 200k – 300k (magas)<br>
    <span style="background:#006d2c; padding:4px 10px;"></span> 300k+ (nagyon magas)

    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_cars))

# ---- LAKOSSÁG LEGEND ----
if show_pop:
    legend_pop = """
    <div style="
        position: fixed; 
        bottom: 50px;
        left: 50px;
        width: 260px;
        background-color: white;
        border-radius: 10px;
        padding: 12px;
        box-shadow: 0 0 12px rgba(0,0,0,0.25);
        font-size: 14px;
        z-index:9999;
    ">
    <b>Lakónépesség (2025)</b><br><br>

    <span style="background:#f1eef6; padding:4px 10px;"></span> 0 – 200k (alacsony)<br>
    <span style="background:#d7b5d8; padding:4px 10px;"></span> 200k – 300k<br>
    <span style="background:#df65b0; padding:4px 10px;"></span> 300k – 400k<br>
    <span style="background:#ce1256; padding:4px 10px;"></span> 400k – 600k<br>
    <span style="background:#91003f; padding:4px 10px;"></span> 600k+ (magas)

    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_pop))

# ---- LIDL SŰRŰSÉG LEGEND ----
if show_lidl_density:
    legend_lidl = """
    <div style="
        position: fixed; 
        bottom: 50px;
        left: 50px;
        width: 260px;
        background-color: white;
        border-radius: 10px;
        padding: 12px;
        box-shadow: 0 0 12px rgba(0,0,0,0.25);
        font-size: 14px;
        z-index:9999;
    ">
    <b>Lidl üzletek / 100k lakos</b><br><br>

    <span style="background:#edf8fb; padding:4px 10px;"></span> 0–2 (alacsony)<br>
    <span style="background:#b2e2e2; padding:4px 10px;"></span> 2–4<br>
    <span style="background:#66c2a4; padding:4px 10px;"></span> 4–6<br>
    <span style="background:#2ca25f; padding:4px 10px;"></span> 6–8<br>
    <span style="background:#08589e; padding:4px 10px;"></span> 8+ (magas)

    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_lidl))

# ---- DISPLAY ----
st_folium(m, width=1400, height=700)