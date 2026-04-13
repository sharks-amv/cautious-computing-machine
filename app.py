from __future__ import annotations

import time

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="BB84 Dashboard", layout="wide")


st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem; padding-bottom: 1.5rem;}
    h1, h2, h3 {letter-spacing: -0.02em;}
    .section-divider {border-top: 1px solid #E5E7EB; margin: 0.6rem 0 1.2rem 0;}
    </style>
    """,
    unsafe_allow_html=True,
)


def section_header(title: str, caption: str | None = None) -> None:
    st.subheader(title)
    if caption:
        st.caption(caption)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def build_attack_probs(min_prob: float, max_prob: float, step: float = 0.1) -> list[float]:
    min_prob = max(0.0, min(1.0, float(min_prob)))
    max_prob = max(0.0, min(1.0, float(max_prob)))
    if max_prob < min_prob:
        min_prob, max_prob = max_prob, min_prob

    vals: list[float] = []
    current = min_prob
    while current <= max_prob + 1e-9:
        vals.append(round(current, 3))
        current += step
    return sorted(set(vals))


@st.cache_data(show_spinner=False)
def run_simulation(
    n_trials: int,
    seed: int,
    qubit_counts: tuple[int, ...],
    attack_probs: tuple[float, ...],
) -> pd.DataFrame:
    import random

    random.seed(seed)

    # Lazy import prevents hard crash at app import time if env is incomplete.
    from bb84_simulation import simulate_bb84

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
                        "n_qubits": int(n_qubits),
                        "attack_prob": float(attack_prob),
                        "qber": float(result["qber"]),
                        "sifted_length": int(result["sifted_length"]),
                        "sifting_ratio": float(result["sifted_length"]) / float(n_qubits),
                    }
                )

    return pd.DataFrame(rows)


def render_sidebar() -> tuple[int, int, tuple[int, ...], tuple[float, ...], bool]:
    st.sidebar.title("Controls")

    n_trials = st.sidebar.slider("Trials", 1, 60, 10)
    seed = st.sidebar.number_input("Seed", min_value=0, max_value=10_000_000, value=42, step=1)

    qubit_options = [100, 250, 500, 750, 1000, 1500, 2000, 3000, 5000]
    selected_qubits = st.sidebar.multiselect(
        "Qubit counts",
        options=qubit_options,
        default=[500, 1000, 2000],
    )

    st.sidebar.caption("Attack probability range")
    min_attack, max_attack = st.sidebar.slider(
        "Range",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 1.0),
        step=0.1,
    )

    attack_probs = build_attack_probs(min_attack, max_attack, step=0.1)

    run_clicked = st.sidebar.button("Run Simulation", type="primary", use_container_width=True)

    return (
        int(n_trials),
        int(seed),
        tuple(sorted(set(selected_qubits))),
        tuple(attack_probs),
        run_clicked,
    )


def render_kpis(df: pd.DataFrame) -> None:
    avg_qber = float(df["qber"].mean())
    max_qber = float(df["qber"].max())
    avg_sifted = float(df["sifted_length"].mean())

    c1, c2, c3 = st.columns(3)
    c1.metric("Avg QBER", f"{avg_qber * 100:.2f}%")
    c2.metric("Max QBER", f"{max_qber * 100:.2f}%")
    c3.metric("Avg Sifted Length", f"{avg_sifted:.1f} bits")


def render_charts(df: pd.DataFrame) -> None:
    line_df = (
        df.groupby(["attack_prob", "n_qubits"], as_index=False)["qber"]
        .mean()
        .sort_values(["n_qubits", "attack_prob"])
    )

    fig_line = px.line(
        line_df,
        x="attack_prob",
        y="qber",
        color="n_qubits",
        markers=True,
        template="plotly_white",
        title="QBER vs Attack Probability",
        labels={"attack_prob": "Attack Probability", "qber": "Mean QBER", "n_qubits": "Qubits"},
    )
    fig_line.update_layout(transition={"duration": 350, "easing": "cubic-in-out"})

    fig_box = px.box(
        df,
        x="attack_prob",
        y="sifted_length",
        color="n_qubits",
        points=False,
        template="plotly_white",
        title="Sifted Key Distribution",
        labels={"attack_prob": "Attack Probability", "sifted_length": "Sifted Length", "n_qubits": "Qubits"},
    )
    fig_box.update_layout(transition={"duration": 350, "easing": "cubic-in-out"})

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_line, use_container_width=True)
    with c2:
        st.plotly_chart(fig_box, use_container_width=True)

    fig_hist = px.histogram(
        df,
        x="qber",
        color="n_qubits",
        barmode="overlay",
        nbins=30,
        opacity=0.65,
        template="plotly_white",
        title="QBER Distribution",
    )
    fig_hist.update_layout(transition={"duration": 350, "easing": "cubic-in-out"})
    st.plotly_chart(fig_hist, use_container_width=True)


def render_table(df: pd.DataFrame) -> None:
    summary = (
        df.groupby(["n_qubits", "attack_prob"], as_index=False)
        .agg(
            trials=("trial", "count"),
            mean_qber=("qber", "mean"),
            max_qber=("qber", "max"),
            mean_sifted=("sifted_length", "mean"),
        )
        .fillna(0.0)
    )

    st.dataframe(summary, use_container_width=True)

    with st.expander("Show trial-level data"):
        st.dataframe(df.sort_values(["n_qubits", "attack_prob", "trial"]), use_container_width=True)


def main() -> None:
    st.title("BB84 Simulation Dashboard")
    st.caption("Stable single-page analytics view for simulation outputs.")

    n_trials, seed, qubit_counts, attack_probs, run_clicked = render_sidebar()

    if "results_df" not in st.session_state:
        st.session_state["results_df"] = pd.DataFrame()

    if run_clicked:
        if not qubit_counts:
            st.warning("Select at least one qubit count before running.")
        elif not attack_probs:
            st.warning("Select a valid attack probability range.")
        else:
            with st.spinner("Running simulations"):
                progress = st.progress(0)
                progress.progress(15)
                time.sleep(0.25)
                try:
                    df = run_simulation(n_trials, seed, qubit_counts, attack_probs)
                except Exception as exc:
                    st.error(f"Simulation failed: {exc}")
                    st.session_state["results_df"] = pd.DataFrame()
                    return
                progress.progress(70)
                time.sleep(0.25)
                st.session_state["results_df"] = df
                progress.progress(100)
                time.sleep(0.2)

    df = st.session_state.get("results_df", pd.DataFrame())
    if df.empty:
        st.info("Use the sidebar controls and click 'Run Simulation' to generate results.")
        return

    section_header("KPI Metrics")
    with st.spinner("Rendering KPIs"):
        render_kpis(df)
        time.sleep(0.2)

    section_header("Charts")
    with st.spinner("Rendering charts"):
        render_charts(df)
        time.sleep(0.2)

    section_header("Data")
    with st.spinner("Rendering table"):
        render_table(df)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
