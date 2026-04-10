from __future__ import annotations

import pandas as pd
import streamlit as st


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def compute_kpis(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {
            "avg_qber": 0.0,
            "avg_sifted_length": 0.0,
            "avg_sifting_ratio": 0.0,
            "detection_rate": 0.0,
        }

    return {
        "avg_qber": float(df["qber"].mean()),
        "avg_sifted_length": float(df["sifted_length"].mean()),
        "avg_sifting_ratio": float(df["sifting_ratio"].mean()),
        "detection_rate": float((df["qber"] > 0.11).mean()),
    }


def render_kpi_row(df: pd.DataFrame) -> None:
    kpis = compute_kpis(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average QBER", _pct(kpis["avg_qber"]))
    col2.metric("Average Sifted Key", f"{kpis['avg_sifted_length']:.1f} bits")
    col3.metric("Average Sifting Ratio", _pct(kpis["avg_sifting_ratio"]))
    col4.metric("Detection Rate", _pct(kpis["detection_rate"]))
