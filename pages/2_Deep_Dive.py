from __future__ import annotations

import time

import pandas as pd
import streamlit as st

from components.charts import qber_histogram, sifted_box_plot
from components.layout import apply_theme, render_global_sidebar, section_header


apply_theme("BB84 Deep Dive")

df, _ = render_global_sidebar()

st.title("Deep Dive")
st.caption("Distribution-level inspection and outlier diagnostics at trial granularity.")

if df.empty:
    st.info("No data loaded. Run the simulation from the sidebar.")
    st.stop()

section_header("Distribution Analysis")
with st.spinner("Rendering distribution views"):
    progress = st.progress(0)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(qber_histogram(df), use_container_width=True)
    progress.progress(50)
    time.sleep(0.08)
    with right:
        st.plotly_chart(sifted_box_plot(df), use_container_width=True)
    progress.progress(100)

section_header("Trial-Level Outliers")
outlier_threshold = float(df["qber"].quantile(0.95)) if not df.empty else 0.0
outliers = df[df["qber"] >= outlier_threshold].copy()
outliers = outliers.sort_values(["qber", "n_qubits", "attack_prob"], ascending=[False, True, True])

st.caption(f"Outliers are defined as QBER greater than or equal to the 95th percentile ({outlier_threshold:.4f}).")

if outliers.empty:
    st.write("No outliers detected for the current selection.")
else:
    st.dataframe(outliers, use_container_width=True)

section_header("Grouped Statistics")
grouped = (
    df.groupby(["n_qubits", "attack_prob"], as_index=False)
    .agg(
        trials=("trial", "count"),
        qber_mean=("qber", "mean"),
        qber_std=("qber", "std"),
        sifted_mean=("sifted_length", "mean"),
    )
    .fillna(0.0)
)
st.dataframe(grouped, use_container_width=True)
