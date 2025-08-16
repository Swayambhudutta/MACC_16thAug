import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="What-If Simulation on the basis of MACC", layout="wide")

# Title
st.title("What-If Simulation on the basis of MACC")

# Sidebar filters
st.sidebar.header("🔍 Filter Projects")

# Load data
def load_data(uploaded_file=None):
    if uploaded_file:
        return pd.read_csv(uploaded_file)
    else:
        # Simulate dummy data
        np.random.seed(42)
        project_types = ['Renewable', 'Efficiency', 'Transport', 'Process', 'Water', 'Buildings']
        irr_values = np.random.uniform(5, 30, 100)
        timeline_values = np.random.choice([0.5, 1.5, 2.5, 4], 100)
        cost_values = np.random.uniform(-200, 2000, 100)
        emissions_saved = np.random.randint(500, 3000, 100)

        return pd.DataFrame({
            'Project Name': [f'Project {i+1}' for i in range(100)],
            'Project Type': np.random.choice(project_types, 100),
            'IRR (%)': irr_values,
            'Timeline (years)': timeline_values,
            'Cost per tonne (₹)': cost_values,
            'Emissions Saved (tCO₂e)': emissions_saved
        })

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload your project list CSV", type=["csv"])
projects = load_data(uploaded_file)

# Define filter bounds
irr_bounds = {'<10%': (0, 10), '10–15%': (10, 15), '15–20%': (15, 20), '>20%': (20, 100)}
timeline_bounds = {'<1 yr': (0, 1), '1–2 yrs': (1, 2), '2–3 yrs': (2, 3), '>3 yrs': (3, 10)}
cost_bounds = {'<0': (-1000, 0), '0–500': (0, 500), '500–1000': (500, 1000), '1000–1500': (1000, 1500), '>1500': (1500, 5000)}
emissions_bounds = {'<1000': (0, 1000), '1000–1500': (1000, 1500), '1500–2000': (1500, 2000), '2000–2500': (2000, 2500), '>2500': (2500, 10000)}

# Sidebar filter inputs
irr_filter = st.sidebar.selectbox("IRR Range", list(irr_bounds.keys()))
type_filter = st.sidebar.multiselect("Project Type", projects['Project Type'].unique(), default=list(projects['Project Type'].unique()))
timeline_filter = st.sidebar.selectbox("Timeline", list(timeline_bounds.keys()))
cost_filter = st.sidebar.selectbox("Cost Range (₹/tonne)", list(cost_bounds.keys()))
emissions_filter = st.sidebar.selectbox("Emissions Saved Range (tCO₂e)", list(emissions_bounds.keys()))

# Filter function
def filter_projects(df, irr_range, types, timeline_range, cost_range, emissions_range):
    return df[
        (df['IRR (%)'].between(*irr_range)) &
        (df['Project Type'].isin(types)) &
        (df['Timeline (years)'].between(*timeline_range)) &
        (df['Cost per tonne (₹)'].between(*cost_range)) &
        (df['Emissions Saved (tCO₂e)'].between(*emissions_range))
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

# Limit to top 10 by emissions saved
if len(filtered) > 10:
    filtered = filtered.sort_values(by='Emissions Saved (tCO₂e)', ascending=False).head(10)
    st.warning("More than 10 projects matched. Showing top 10 by emissions saved.")

# MACC Chart
st.subheader("📊 Marginal Abatement Cost Curve (MACC)")
color_scale = ['#2ca02c', '#ff7f0e', '#d62728']  # Green, Orange, Red
fig = px.bar(
    filtered,
    x='Emissions Saved (tCO₂e)',
    y='Cost per tonne (₹)',
    color='IRR (%)',
    color_continuous_scale=color_scale,
    hover_data=['Project Name', 'Project Type', 'Timeline (years)'],
    labels={'Cost per tonne (₹)': 'Marginal Cost (₹/tCO₂e)', 'Emissions Saved (tCO₂e)': 'Emissions Reduced (tCO₂e)'},
    title="MACC Curve for Selected Projects"
)
st.plotly_chart(fig, use_container_width=True)

# Simulation Panel
st.subheader("🧪 Simulation Panel")

col1, col2, col3 = st.columns(3)
with col1:
    sim_irr = st.selectbox("Simulate IRR Range", list(irr_bounds.keys()), key='sim_irr')
with col2:
    sim_types = st.multiselect("Simulate Project Type", projects['Project Type'].unique(), default=list(projects['Project Type'].unique()), key='sim_types')
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
