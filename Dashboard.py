import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="VRP Dashboard", layout="wide")

DEPOT_ZIP = 1887

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_locations():
    df = pd.read_excel("deliveries.xlsx", sheet_name="LocationTable")
    # Drop rows where 'ZIP' is NaN before converting to int
    df.dropna(subset=['ZIP'], inplace=True)
    df["ZIP"] = df["ZIP"].astype(int)
    return df

@st.cache_data
def load_solution(file):
    xls = pd.ExcelFile(file)
    # Set header to 2 to correctly parse column names from the third row
    summary = pd.read_excel(xls, "Day Summary", header=2)
    routes = pd.read_excel(xls, "Route Details")
    return summary, routes


locations = load_locations()

# create coordinate map
coord_map = {
    row["ZIP"]: (row["X"], row["Y"])
    for _, row in locations.iterrows()
}

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("VRP Dashboard")
scenario_file = st.sidebar.selectbox(
    "Select Scenario",
    [
        "solution_Q1_BaseCase.xlsx",
        "solution_Q2_MixedFleet.xlsx",
        "solution_Q3_Relaxed.xlsx",
    ],
)

summary, routes = load_solution(scenario_file)

st.title("🚚 Vehicle Routing Problem Dashboard (NHG Project)")

# -----------------------------
# KPIs
# -----------------------------
total_miles = summary["Total Miles"].sum()
total_routes = summary["Routes"].sum()
total_orders = summary["Orders"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Weekly Miles", f"{total_miles:,.1f}")
col2.metric("Total Routes", int(total_routes))
col3.metric("Total Orders", int(total_orders))

# -----------------------------
# DAILY PERFORMANCE
# -----------------------------
st.subheader("📊 Daily Performance")

fig = px.bar(
    summary,
    x="Day",
    y="Total Miles",
    color="Day",
    text="Total Miles",
)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# ROUTE FILTER
# -----------------------------
st.subheader("🗺️ Route Visualization")

day_selected = st.selectbox("Choose Day", routes["Day"].unique())
route_ids = routes[routes["Day"] == day_selected]["Route"].unique()

route_selected = st.selectbox("Choose Route", route_ids)

route_data = routes[
    (routes["Day"] == day_selected) &
    (routes["Route"] == route_selected)
]

# -----------------------------
# BUILD ROUTE PATH
# -----------------------------
def build_route_path(df):
    path = []

    for _, row in df.iterrows():
        zip_code = row["ZIP"]
        if zip_code in coord_map:
            path.append(coord_map[zip_code])

    return path


route_path = build_route_path(route_data)

# add depot start/end
if DEPOT_ZIP in coord_map:
    depot = coord_map[DEPOT_ZIP]
    route_path = [depot] + route_path + [depot]

lats = [p[0] for p in route_path]
lons = [p[1] for p in route_path]

# -----------------------------
# MAP PLOT
# -----------------------------
fig_map = go.Figure()

fig_map.add_trace(
    go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode="markers+lines",
        marker=dict(size=8),
        line=dict(width=2),
        name="Route"
    )
)

fig_map.update_layout(
    mapbox_style="open-street-map",
    mapbox_zoom=5,
    mapbox_center={"lat": np.mean(lats), "lon": np.mean(lons)},
    margin={"r":0,"t":0,"l":0,"b":0}
)

st.plotly_chart(fig_map, use_container_width=True)

# -----------------------------
# ROUTE DETAILS TABLE
# -----------------------------
st.subheader("📦 Route Stop Details")
st.dataframe(route_data)

# -----------------------------
# SUMMARY INSIGHT
# -----------------------------
st.subheader("📌 Insights")

avg_miles = summary["Total Miles"].mean()
best_day = summary.loc[summary["Total Miles"].idxmin(), "Day"]
best_day = summary.loc[summary["Total Miles"].idxmin(), "Day"]
worst_day = summary.loc[summary["Total Miles"].idxmax(), "Day"]

st.write(f"""
- Average daily miles: **{avg_miles:.1f}**
- Most efficient day: **{best_day}**
- Highest workload day: **{worst_day}**
"""
)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("Built for IE 7200 VRP Final Project | NHG Logistics Optimization")
