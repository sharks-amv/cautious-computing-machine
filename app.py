from __future__ import annotations

import time

import streamlit as st

from components.charts import qber_heatmap, qber_line_chart
from components.kpis import render_kpi_row
from components.layout import apply_theme, render_global_sidebar, section_header


apply_theme("BB84 Overview")

df, config = render_global_sidebar()

st.title("BB84 Analytics Overview")
st.caption("High-level simulation insights using shared controls and cached runs.")

if df.empty:
    st.info("No simulation data available. Configure inputs in the sidebar and run the simulation.")
    st.stop()

section_header("Key Metrics")
with st.spinner("Rendering KPI summary"):
    progress = st.progress(0)
    render_kpi_row(df)
    progress.progress(100)
    time.sleep(0.06)

section_header("Summary Charts")
with st.spinner("Rendering summary charts"):
    progress = st.progress(0)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(qber_line_chart(df), use_container_width=True)
    progress.progress(55)
    time.sleep(0.08)
    with col2:
        st.plotly_chart(qber_heatmap(df), use_container_width=True)
    progress.progress(100)
    time.sleep(0.06)

section_header("Quick Insights")
agg = (
    df.groupby("attack_prob", as_index=False)["qber"]
    .mean()
    .sort_values("attack_prob")
)
qber_change = float(agg["qber"].iloc[-1] - agg["qber"].iloc[0]) if len(agg) > 1 else 0.0

c1, c2, c3 = st.columns(3)
c1.markdown(
    f"""
    <div class="insight-card">
      <div class="insight-title">Configuration</div>
      <div class="insight-value">{len(config.qubit_counts)} qubit tiers, {config.n_trials} trials</div>
    </div>
    """,
    unsafe_allow_html=True,
)
c2.markdown(
    f"""
    <div class="insight-card">
      <div class="insight-title">Attack Window</div>
      <div class="insight-value">{config.attack_prob_min:.2f} to {config.attack_prob_max:.2f}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
c3.markdown(
    f"""
    <div class="insight-card">
      <div class="insight-title">QBER Shift Across Window</div>
      <div class="insight-value">{qber_change * 100:.2f}%</div>
    </div>
    """,
    unsafe_allow_html=True,
)
