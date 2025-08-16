import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------
# Generate Synthetic Data (100 Projects)
# ---------------------------
np.random.seed(42)

project_types = ["Renewable", "Efficiency", "Transport", "Process", "Water", "Buildings"]
timeline_categories = ["<1 yr", "1–2 yrs", "2–3 yrs", ">3 yrs"]

data = {
    "Project": [f"Project {i+1}" for i in range(100)],
    "IRR": np.random.uniform(5, 25, 100),  # IRR between 5% and 25%
    "Project Type": np.random.choice(project_types, 100),
    "Timeline": np.random.choice(timeline_categories, 100),
    "Cost (₹/tCO2e)": np.random.uniform(-200, 2000, 100),  # can be negative
    "Emissions Saved (tCO2e)": np.random.uniform(500, 3000, 100)
}

df = pd.DataFrame(data)

# ---------------------------
# Streamlit App
# ---------------------------
st.title("What-If Simulation on the basis of MACC")

st.markdown("### 📊 Marginal Abatement Cost Curve (MACC)")

# ---------------------------
# Filters
# ---------------------------
with st.expander("🔍 Apply Filters"):
    irr_filter = st.radio("IRR Range", ["All", "<10%", "10–15%", "15–20%", ">20%"], index=0)
    type_filter = st.multiselect("Project Type", ["All"] + project_types, default=["All"])
    timeline_filter = st.multiselect("Timeline", ["All"] + timeline_categories, default=["All"])
    cost_filter = st.radio("Cost Range (₹/tCO₂e)", ["All", "<0", "0–500", "500–1000", "1000–1500", ">1500"], index=0)
    emissions_filter = st.radio("Emissions Saved Range (tCO₂e)", ["All", "<1000", "1000–1500", "1500–2000", "2000–2500", ">2500"], index=0)

filtered_df = df.copy()

# Apply IRR filter
if irr_filter != "All":
    if irr_filter == "<10%":
        filtered_df = filtered_df[filtered_df["IRR"] < 10]
    elif irr_filter == "10–15%":
        filtered_df = filtered_df[(filtered_df["IRR"] >= 10) & (filtered_df["IRR"] < 15)]
    elif irr_filter == "15–20%":
        filtered_df = filtered_df[(filtered_df["IRR"] >= 15) & (filtered_df["IRR"] < 20)]
    else:
        filtered_df = filtered_df[filtered_df["IRR"] >= 20]

# Apply Project Type
if "All" not in type_filter:
    filtered_df = filtered_df[filtered_df["Project Type"].isin(type_filter)]

# Apply Timeline
if "All" not in timeline_filter:
    filtered_df = filtered_df[filtered_df["Timeline"].isin(timeline_filter)]

# Apply Cost Range
if cost_filter != "All":
    if cost_filter == "<0":
        filtered_df = filtered_df[filtered_df["Cost (₹/tCO2e)"] < 0]
    elif cost_filter == "0–500":
        filtered_df = filtered_df[(filtered_df["Cost (₹/tCO2e)"] >= 0) & (filtered_df["Cost (₹/tCO2e)"] < 500)]
    elif cost_filter == "500–1000":
        filtered_df = filtered_df[(filtered_df["Cost (₹/tCO2e)"] >= 500) & (filtered_df["Cost (₹/tCO2e)"] < 1000)]
    elif cost_filter == "1000–1500":
        filtered_df = filtered_df[(filtered_df["Cost (₹/tCO2e)"] >= 1000) & (filtered_df["Cost (₹/tCO2e)"] < 1500)]
    else:
        filtered_df = filtered_df[filtered_df["Cost (₹/tCO2e)"] >= 1500]

# Apply Emissions Range
if emissions_filter != "All":
    if emissions_filter == "<1000":
        filtered_df = filtered_df[filtered_df["Emissions Saved (tCO2e)"] < 1000]
    elif emissions_filter == "1000–1500":
        filtered_df = filtered_df[(filtered_df["Emissions Saved (tCO2e)"] >= 1000) & (filtered_df["Emissions Saved (tCO2e)"] < 1500)]
    elif emissions_filter == "1500–2000":
        filtered_df = filtered_df[(filtered_df["Emissions Saved (tCO2e)"] >= 1500) & (filtered_df["Emissions Saved (tCO2e)"] < 2000)]
    elif emissions_filter == "2000–2500":
        filtered_df = filtered_df[(filtered_df["Emissions Saved (tCO2e)"] >= 2000) & (filtered_df["Emissions Saved (tCO2e)"] < 2500)]
    else:
        filtered_df = filtered_df[filtered_df["Emissions Saved (tCO2e)"] >= 2500]

# ---------------------------
# Handle Top 10 Rule
# ---------------------------
show_df = filtered_df.copy()
disclaimer = ""

if len(show_df) > 10:
    show_df = show_df.nlargest(10, "Emissions Saved (tCO2e)")
    disclaimer = "⚠️ More than 10 projects matched. Showing **Top 10** projects by Emissions Saved."

# ---------------------------
# MACC Graph
# ---------------------------
if not show_df.empty:
    fig = px.bar(
        show_df.sort_values("Cost (₹/tCO2e)"),
        x="Emissions Saved (tCO2e)",
        y="Cost (₹/tCO2e)",
        color="Project Type",
        hover_data=["Project", "IRR", "Timeline"],
        text="Project",
        title="MACC Curve"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No projects found for selected filters.")

if disclaimer:
    st.info(disclaimer)

# ---------------------------
# Simulation Section
# ---------------------------
st.markdown("## 🧮 Run a What-If Simulation")

with st.form("simulation_form"):
    sim_irr = st.selectbox("IRR Range", ["All", "<10%", "10–15%", "15–20%", ">20%"])
    sim_type = st.multiselect("Project Type", project_types)
    sim_timeline = st.multiselect("Timeline", timeline_categories)
    sim_cost = st.selectbox("Cost Range (₹/tCO₂e)", ["All", "<0", "0–500", "500–1000", "1000–1500", ">1500"])
    sim_emissions = st.selectbox("Emissions Saved Range (tCO₂e)", ["All", "<1000", "1000–1500", "1500–2000", "2000–2500", ">2500"])

    submitted = st.form_submit_button("Simulate")

    if submitted:
        sim_df = df.copy()

        # Apply filters again
        if sim_irr != "All":
            if sim_irr == "<10%":
                sim_df = sim_df[sim_df["IRR"] < 10]
            elif sim_irr == "10–15%":
                sim_df = sim_df[(sim_df["IRR"] >= 10) & (sim_df["IRR"] < 15)]
            elif sim_irr == "15–20%":
                sim_df = sim_df[(sim_df["IRR"] >= 15) & (sim_df["IRR"] < 20)]
            else:
                sim_df = sim_df[sim_df["IRR"] >= 20]

        if sim_type:
            sim_df = sim_df[sim_df["Project Type"].isin(sim_type)]

        if sim_timeline:
            sim_df = sim_df[sim_df["Timeline"].isin(sim_timeline)]

        if sim_cost != "All":
            if sim_cost == "<0":
                sim_df = sim_df[sim_df["Cost (₹/tCO2e)"] < 0]
            elif sim_cost == "0–500":
                sim_df = sim_df[(sim_df["Cost (₹/tCO2e)"] >= 0) & (sim_df["Cost (₹/tCO2e)"] < 500)]
            elif sim_cost == "500–1000":
                sim_df = sim_df[(sim_df["Cost (₹/tCO2e)"] >= 500) & (sim_df["Cost (₹/tCO2e)"] < 1000)]
            elif sim_cost == "1000–1500":
                sim_df = sim_df[(sim_df["Cost (₹/tCO2e)"] >= 1000) & (sim_df["Cost (₹/tCO2e)"] < 1500)]
            else:
                sim_df = sim_df[sim_df["Cost (₹/tCO2e)"] >= 1500]

        if sim_emissions != "All":
            if sim_emissions == "<1000":
                sim_df = sim_df[sim_df["Emissions Saved (tCO2e)"] < 1000]
            elif sim_emissions == "1000–1500":
                sim_df = sim_df[(sim_df["Emissions Saved (tCO2e)"] >= 1000) & (sim_df["Emissions Saved (tCO2e)"] < 1500)]
            elif sim_emissions == "1500–2000":
                sim_df = sim_df[(sim_df["Emissions Saved (tCO2e)"] >= 1500) & (sim_df["Emissions Saved (tCO2e)"] < 2000)]
            elif sim_emissions == "2000–2500":
                sim_df = sim_df[(sim_df["Emissions Saved (tCO2e)"] >= 2000) & (sim_df["Emissions Saved (tCO2e)"] < 2500)]
            else:
                sim_df = sim_df[sim_df["Emissions Saved (tCO2e)"] >= 2500]

        st.write("### 🎯 Projects Matching Simulation")
        st.dataframe(sim_df.reset_index(drop=True))
