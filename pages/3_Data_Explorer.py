from __future__ import annotations

import time

import streamlit as st

from components.layout import apply_theme, render_global_sidebar, section_header


apply_theme("BB84 Data Explorer")

df, _ = render_global_sidebar()

st.title("Data Explorer")
st.caption("Filter, inspect, and export the complete simulation dataset.")

if df.empty:
    st.info("No data loaded. Run the simulation from the sidebar.")
    st.stop()

section_header("Filters")
q_options = sorted(df["n_qubits"].unique().tolist())
a_options = sorted(df["attack_prob"].unique().tolist())

col1, col2 = st.columns(2)
with col1:
    q_filter = st.multiselect("Qubit counts", q_options, default=q_options)
with col2:
    a_filter = st.multiselect("Attack probabilities", a_options, default=a_options)

filtered = df[df["n_qubits"].isin(q_filter) & df["attack_prob"].isin(a_filter)].copy()

section_header("Table")
with st.spinner("Loading table"):
    progress = st.progress(0)
    time.sleep(0.05)
    progress.progress(35)
    st.dataframe(filtered.sort_values(["n_qubits", "attack_prob", "trial"]), use_container_width=True)
    progress.progress(100)

section_header("Download")
csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered CSV",
    data=csv_data,
    file_name="bb84_filtered_results.csv",
    mime="text/csv",
)
