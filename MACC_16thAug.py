import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import re

st.set_page_config(page_title="What-If Simulation on the basis of MACC", layout="wide")
st.title("What-If Simulation on the basis of MACC")
st.sidebar.header("🔍 Filter Projects")

# Load and normalize data
def normalize_columns(df):
    df.columns = [re.sub(r'[^\\w\\s]', '', col).strip().lower().replace(" ", "_") for col in df.columns]
    return df

uploaded_file = st.sidebar.file_uploader("Upload your project list CSV", type=["csv"])
if uploaded_file:
    projects = pd.read_csv(uploaded_file)
    projects = normalize_columns(projects)
else:
    st.warning("Please upload a project list CSV file to proceed.")
    st.stop()

# Column names from your file
# ['project_name', 'project_type', 'irr', 'timeline_years', 'cost_per_tonne', 'emissions_saved_tco₂e']

# Define filter bounds
irr_bounds = {'<10%': (0, 10), '10–15%': (10, 15), '15–20%': (15, 20), '>20%': (20, 100)}
timeline_bounds = {'<1 yr': (0, 1), '1–2 yrs': (1, 2), '2–3 yrs': (2, 3), '>3 yrs': (3, 10)}
cost_bounds = {'<0': (-1000, 0), '0–500': (0, 500), '500–1000': (500, 1000), '1000–1500': (1000, 1500), '>1500': (1500, 5000)}
emissions_bounds = {'<1000': (0, 1000), '1000–1500': (1000, 1500), '1500–2000': (1500, 2000), '2000–2500': (2000, 2500), '>2500': (2500, 10000)}

# Sidebar filters with Select All
irr_filter = st.sidebar.selectbox("IRR Range", list(irr_bounds.keys()))
type_options = sorted(projects['project_type'].dropna().unique())
type_filter = st.sidebar.multiselect("Project Type", ['Select All'] + type_options, default=['Select All'])
if 'Select All' in type_filter:
    type_filter = type_options

timeline_filter = st.sidebar.selectbox("Timeline", list(timeline_bounds.keys()))
cost_filter = st.sidebar.selectbox("Cost Range (₹/tonne)", list(cost_bounds.keys()))
emissions_filter = st.sidebar.selectbox("Emissions Saved Range (tCO₂e)", list(emissions_bounds.keys()))
top_n = st.sidebar.selectbox("Show Top Projects", [10, 20, 30])

# Filter function
def filter_projects(df, irr_range, types, timeline_range, cost_range, emissions_range):
    return df[
        (df['irr'].between(*irr_range)) &
        (df['project_type'].isin(types)) &
        (df['timeline_years'].between(*timeline_range)) &
        (df['cost_per_tonne'].between(*cost_range)) &
        (df['emissions_saved_tco₂e'].between(*emissions_range))
    ]

# Apply filters
filtered = filter_projects(
    projects,
    irr_bounds[irr_filter],
    type_filter,
    timeline_bounds[timeline_filter],
    cost_bounds[cost_filter],
    emissions_bounds[emissions_filter]
)

# Limit to top N
if len(filtered) > top_n:
    filtered = filtered.sort_values(by='emissions_saved_tco₂e', ascending=False).head(top_n)
    st.warning(f"More than {top_n} projects matched. Showing top {top_n} by emissions saved.")

# MACC Chart
st.subheader("📊 Marginal Abatement Cost Curve (MACC)")
if not filtered.empty:
    filtered = filtered.sort_values(by='cost_per_tonne')
    fig = px.bar(
        filtered,
        x='project_name',
        y='cost_per_tonne',
        color='irr',
        color_continuous_scale=['#2ca02c', '#ff7f0e', '#d62728'],
        hover_data=['project_type', 'timeline_years', 'emissions_saved_tco₂e'],
        labels={'cost_per_tonne': 'Marginal Cost (₹/tCO₂e)', 'project_name': 'Project'},
        title="MACC Curve for Selected Projects"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No projects match the selected filters.")

# Simulation Panel
st.subheader("🧪 Simulation Panel")
col1, col2, col3 = st.columns(3)
with col1:
    sim_irr = st.selectbox("Simulate IRR Range", list(irr_bounds.keys()), key='sim_irr')
with col2:
    sim_types = st.multiselect("Simulate Project Type", ['Select All'] + type_options, default=['Select All'], key='sim_types')
    if 'Select All' in sim_types:
        sim_types = type_options
with col3:
    sim_timeline = st.selectbox("Simulate Timeline", list(timeline_bounds.keys()), key='sim_timeline')

col4, col5 = st.columns(2)
with col4:
    sim_cost = st.selectbox("Simulate Cost Range", list(cost_bounds.keys()), key='sim_cost')
with col5:
    sim_emissions = st.selectbox("Simulate Emissions Range", list(emissions_bounds.keys()), key='sim_emissions')

if st.button("Simulate"):
    sim_filtered = filter_projects(
        projects,
        irr_bounds[sim_irr],
        sim_types,
        timeline_bounds[sim_timeline],
        cost_bounds[sim_cost],
        emissions_bounds[sim_emissions]
    )
    st.markdown(f"### 📋 Simulation Results ({len(sim_filtered)} projects found)")
    st.dataframe(sim_filtered.reset_index(drop=True))
