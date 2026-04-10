from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PALETTE = ["#111827", "#374151", "#6B7280", "#9CA3AF", "#D1D5DB"]


def _base_layout(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        height=height,
        template="plotly_white",
        font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#111827"),
        legend=dict(title=None, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=50, b=10),
        transition={"duration": 450, "easing": "cubic-in-out"},
    )
    fig.update_xaxes(gridcolor="#F3F4F6")
    fig.update_yaxes(gridcolor="#F3F4F6")
    return fig


def qber_line_chart(df: pd.DataFrame) -> go.Figure:
    line_df = (
        df.groupby(["attack_prob", "n_qubits"], as_index=False)["qber"]
        .mean()
        .sort_values(["n_qubits", "attack_prob"])
    )
    fig = px.line(
        line_df,
        x="attack_prob",
        y="qber",
        color="n_qubits",
        markers=True,
        color_discrete_sequence=PALETTE,
        labels={"attack_prob": "Attack Probability", "qber": "Mean QBER", "n_qubits": "Qubits"},
        title="QBER vs Attack Probability",
    )
    fig.add_hline(y=0.25, line_dash="dot", line_color="#9CA3AF")
    return _base_layout(fig)


def qber_heatmap(df: pd.DataFrame) -> go.Figure:
    heat_df = (
        df.groupby(["n_qubits", "attack_prob"], as_index=False)["qber"]
        .mean()
        .pivot(index="n_qubits", columns="attack_prob", values="qber")
    )
    fig = px.imshow(
        heat_df,
        aspect="auto",
        color_continuous_scale=[[0, "#F9FAFB"], [1, "#111827"]],
        origin="lower",
        labels={"x": "Attack Probability", "y": "Qubits", "color": "QBER"},
        title="QBER Heatmap",
    )
    return _base_layout(fig)


def sifted_box_plot(df: pd.DataFrame) -> go.Figure:
    fig = px.box(
        df,
        x="attack_prob",
        y="sifted_length",
        color="n_qubits",
        color_discrete_sequence=PALETTE,
        points=False,
        labels={"attack_prob": "Attack Probability", "sifted_length": "Sifted Key Length", "n_qubits": "Qubits"},
        title="Sifted Key Length Distribution",
    )
    return _base_layout(fig)


def qber_histogram(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df,
        x="qber",
        color="n_qubits",
        color_discrete_sequence=PALETTE,
        nbins=35,
        barmode="overlay",
        opacity=0.65,
        title="QBER Distribution",
    )
    return _base_layout(fig)


def trial_trend(df: pd.DataFrame) -> go.Figure:
    trend_df = (
        df.groupby(["trial", "n_qubits"], as_index=False)["qber"]
        .mean()
        .sort_values(["trial", "n_qubits"])
    )
    fig = px.line(
        trend_df,
        x="trial",
        y="qber",
        color="n_qubits",
        markers=True,
        color_discrete_sequence=PALETTE,
        title="Trial Trend Comparison",
        labels={"trial": "Trial", "qber": "Mean QBER", "n_qubits": "Qubits"},
    )
    return _base_layout(fig)
