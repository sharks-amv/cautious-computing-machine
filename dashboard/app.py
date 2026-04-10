"""Streamlit dashboard for BB84 simulation analysis.

Non-invasive addition: reuses existing simulation logic from bb84_simulation.py.
Run with:
    streamlit run dashboard/app.py
"""

from __future__ import annotations

import math
from typing import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st

from bb84_simulation import simulate_bb84


st.set_page_config(page_title="BB84 Dashboard", page_icon="🔐", layout="wide")


@st.cache_data(show_spinner=False)
def run_simulation_grid(
    qubit_counts: tuple[int, ...],
    attack_probs: tuple[float, ...],
    n_trials: int,
    random_seed: int,
) -> pd.DataFrame:
    """Run a simulation grid and return trial-level records as a DataFrame."""
    # Seed random module used by simulation to keep runs reproducible per session.
    import random

    random.seed(random_seed)

    rows: list[dict[str, float | int | bool]] = []
    for n_qubits in qubit_counts:
        for attack_prob in attack_probs:
            eve_present = attack_prob > 0.0
            for trial in range(1, n_trials + 1):
                result = simulate_bb84(
                    n_qubits=n_qubits,
                    eve_present=eve_present,
                    eve_attack_prob=attack_prob,
                )
                rows.append(
                    {
                        "trial": trial,
                        "n_qubits": n_qubits,
                        "attack_prob": round(float(attack_prob), 3),
                        "eve_present": eve_present,
                        "qber": float(result["qber"]),
                        "sifted_length": int(result["sifted_length"]),
                        "sifting_ratio": (
                            float(result["sifted_length"]) / n_qubits if n_qubits else math.nan
                        ),
                    }
                )
    return pd.DataFrame(rows)


def _format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def _sorted_unique(values: Iterable[float]) -> list[float]:
    return sorted(set(float(v) for v in values))


def render_header() -> None:
    st.title("🔐 BB84 Quantum Key Distribution Dashboard")
    st.caption(
        "Interactive analytics over the existing `simulate_bb84` pipeline "
        "from this repository."
    )


def render_sidebar() -> tuple[tuple[int, ...], tuple[float, ...], int, int]:
    st.sidebar.header("Simulation Controls")

    qubit_options = [100, 250, 500, 1000, 2000, 5000]
    selected_qubits = st.sidebar.multiselect(
        "Qubit counts",
        options=qubit_options,
        default=[500, 1000, 2000],
        help="Number of qubits Alice sends per simulation.",
    )

    attack_options = [round(i * 0.1, 1) for i in range(0, 11)]
    selected_attack = st.sidebar.multiselect(
        "Eve attack probability",
        options=attack_options,
        default=[0.0, 0.5, 1.0],
        format_func=lambda x: f"{int(x * 100)}%",
    )

    n_trials = st.sidebar.slider("Trials per setting", 1, 50, 10)
    random_seed = st.sidebar.number_input(
        "Random seed", min_value=0, max_value=1_000_000, value=42, step=1
    )

    if not selected_qubits:
        st.sidebar.warning("Select at least one qubit count.")
    if not selected_attack:
        st.sidebar.warning("Select at least one attack probability.")

    return tuple(selected_qubits), tuple(selected_attack), n_trials, int(random_seed)


def render_kpis(df: pd.DataFrame) -> None:
    avg_qber = df["qber"].mean()
    avg_sifted = df["sifted_length"].mean()
    avg_ratio = df["sifting_ratio"].mean()
    detection_rate = (df["qber"] > 0.11).mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg QBER", _format_percent(avg_qber))
    c2.metric("Avg Sifted Length", f"{avg_sifted:.1f} bits")
    c3.metric("Avg Sifting Ratio", _format_percent(avg_ratio))
    c4.metric("Trials Above 11% QBER", _format_percent(detection_rate))


def render_charts(df: pd.DataFrame) -> None:
    st.subheader("QBER Trends")

    qber_line = (
        df.groupby(["attack_prob", "n_qubits"], as_index=False)["qber"]
        .mean()
        .sort_values(["n_qubits", "attack_prob"])
    )
    fig_line = px.line(
        qber_line,
        x="attack_prob",
        y="qber",
        color="n_qubits",
        markers=True,
        title="Mean QBER vs Attack Probability",
        labels={"attack_prob": "Attack Probability", "qber": "Mean QBER", "n_qubits": "Qubits"},
    )
    fig_line.add_hline(y=0.25, line_dash="dash", line_color="red", annotation_text="25% theoretical max")
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Sifted Key Behavior")

    fig_box = px.box(
        df,
        x="attack_prob",
        y="sifted_length",
        color="n_qubits",
        points=False,
        title="Sifted Key Length Distribution",
        labels={"attack_prob": "Attack Probability", "sifted_length": "Sifted Key Length", "n_qubits": "Qubits"},
    )
    st.plotly_chart(fig_box, use_container_width=True)

    heat_df = (
        df.groupby(["n_qubits", "attack_prob"], as_index=False)["qber"]
        .mean()
        .pivot(index="n_qubits", columns="attack_prob", values="qber")
    )
    fig_heat = px.imshow(
        heat_df,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        origin="lower",
        title="QBER Heatmap (Mean across Trials)",
        labels={"x": "Attack Probability", "y": "Qubits", "color": "QBER"},
    )
    st.plotly_chart(fig_heat, use_container_width=True)


def render_tables(df: pd.DataFrame) -> None:
    st.subheader("Detailed Results")

    summary = (
        df.groupby(["n_qubits", "attack_prob"], as_index=False)
        .agg(
            trials=("trial", "count"),
            mean_qber=("qber", "mean"),
            std_qber=("qber", "std"),
            mean_sifted=("sifted_length", "mean"),
            mean_ratio=("sifting_ratio", "mean"),
        )
        .fillna(0.0)
    )
    st.dataframe(summary, use_container_width=True)

    with st.expander("View trial-level data"):
        st.dataframe(df.sort_values(["n_qubits", "attack_prob", "trial"]), use_container_width=True)


def main() -> None:
    render_header()
    qubits, attack_probs, n_trials, random_seed = render_sidebar()

    if not qubits or not attack_probs:
        st.info("Choose at least one qubit count and one attack probability to run simulations.")
        return

    with st.spinner("Running BB84 simulations..."):
        df = run_simulation_grid(
            qubit_counts=tuple(sorted(set(qubits))),
            attack_probs=tuple(_sorted_unique(attack_probs)),
            n_trials=n_trials,
            random_seed=random_seed,
        )

    if df.empty:
        st.warning("No simulation data produced. Please adjust filters and try again.")
        return

    render_kpis(df)
    render_charts(df)
    render_tables(df)


if __name__ == "__main__":
    main()
