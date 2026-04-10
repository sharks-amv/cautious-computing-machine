from __future__ import annotations

import time

import streamlit as st

from components.charts import qber_heatmap, qber_line_chart, trial_trend
from components.layout import apply_theme, render_global_sidebar, section_header


apply_theme("BB84 Analytics")

df, _ = render_global_sidebar()

st.title("Analytics")
st.caption("Comparative trend analysis across attack probability and qubit scales.")

if df.empty:
    st.info("No data loaded. Run the simulation from the sidebar.")
    st.stop()

section_header("QBER and Trend Comparisons")
with st.spinner("Rendering analytics charts"):
    progress = st.progress(0)
    top_left, top_right = st.columns(2)
    with top_left:
        st.plotly_chart(qber_line_chart(df), use_container_width=True)
    progress.progress(45)
    time.sleep(0.07)
    with top_right:
        st.plotly_chart(qber_heatmap(df), use_container_width=True)
    progress.progress(80)
    time.sleep(0.06)
    st.plotly_chart(trial_trend(df), use_container_width=True)
    progress.progress(100)

section_header("Trend Summary")
trend_summary = (
    df.groupby(["n_qubits", "attack_prob"], as_index=False)["qber"]
    .mean()
    .sort_values(["n_qubits", "attack_prob"])
)
st.dataframe(trend_summary, use_container_width=True)
