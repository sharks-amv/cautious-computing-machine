from __future__ import annotations

import time

import pandas as pd
import streamlit as st

from utils.simulation import (
    SimulationConfig,
    get_active_dataframe,
    get_default_config,
    run_simulation_cached,
)


def apply_theme(page_title: str) -> None:
    st.set_page_config(page_title=page_title, layout="wide")
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.2rem; padding-bottom: 1.5rem;}
        h1, h2, h3 {letter-spacing: -0.02em;}
        .subtle-divider {border-top: 1px solid #E5E7EB; margin: 0.6rem 0 1.2rem 0;}
        .insight-card {
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 0.9rem 1rem;
            background: #FFFFFF;
        }
        .insight-title {font-size: 0.82rem; color: #6B7280; margin-bottom: 0.2rem;}
        .insight-value {font-size: 1.05rem; color: #111827; font-weight: 600;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, caption: str | None = None) -> None:
    st.subheader(title)
    if caption:
        st.caption(caption)
    st.markdown('<div class="subtle-divider"></div>', unsafe_allow_html=True)


def render_global_sidebar() -> tuple[pd.DataFrame, SimulationConfig]:
    st.sidebar.title("Simulation Controls")

    defaults = st.session_state.get("simulation_config", get_default_config())

    n_trials = st.sidebar.slider("Trials", min_value=1, max_value=60, value=defaults.n_trials)
    random_seed = st.sidebar.number_input(
        "Random seed", min_value=0, max_value=10_000_000, value=defaults.random_seed, step=1
    )

    qubit_choices = [100, 250, 500, 750, 1000, 1500, 2000, 3000, 5000]
    selected_qubits = st.sidebar.multiselect(
        "Qubit counts",
        options=qubit_choices,
        default=list(defaults.qubit_counts),
    )

    st.sidebar.caption("Attack probability range")
    attack_min, attack_max = st.sidebar.slider(
        "Min and Max",
        min_value=0.0,
        max_value=1.0,
        value=(float(defaults.attack_prob_min), float(defaults.attack_prob_max)),
        step=0.05,
    )
    attack_step = st.sidebar.select_slider(
        "Step",
        options=[0.05, 0.1, 0.2, 0.25],
        value=float(defaults.attack_prob_step),
    )

    config = SimulationConfig(
        n_trials=int(n_trials),
        random_seed=int(random_seed),
        qubit_counts=tuple(sorted(set(selected_qubits))),
        attack_prob_min=float(attack_min),
        attack_prob_max=float(attack_max),
        attack_prob_step=float(attack_step),
    )

    if st.sidebar.button("Run Simulation", type="primary", use_container_width=True):
        if not config.qubit_counts:
            st.sidebar.warning("Select at least one qubit count.")
        else:
            with st.spinner("Running simulation grid"):
                progress = st.sidebar.progress(0)
                progress.progress(20)
                time.sleep(0.08)
                st.session_state["simulation_config"] = config
                df = run_simulation_cached(config)
                progress.progress(70)
                time.sleep(0.08)
                st.session_state["simulation_df"] = df
                progress.progress(100)
                time.sleep(0.05)

    if "simulation_df" not in st.session_state:
        if config.qubit_counts:
            st.session_state["simulation_config"] = config
            st.session_state["simulation_df"] = run_simulation_cached(config)

    return get_active_dataframe(), st.session_state.get("simulation_config", config)
