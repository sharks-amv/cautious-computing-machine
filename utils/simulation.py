from __future__ import annotations

import random
from dataclasses import dataclass

import pandas as pd
import streamlit as st

from bb84_simulation import simulate_bb84


@dataclass(frozen=True)
class SimulationConfig:
    n_trials: int
    random_seed: int
    qubit_counts: tuple[int, ...]
    attack_prob_min: float
    attack_prob_max: float
    attack_prob_step: float


def build_attack_probabilities(min_prob: float, max_prob: float, step: float) -> tuple[float, ...]:
    min_prob = max(0.0, min(1.0, float(min_prob)))
    max_prob = max(0.0, min(1.0, float(max_prob)))
    if max_prob < min_prob:
        min_prob, max_prob = max_prob, min_prob

    step = max(0.01, float(step))
    values: list[float] = []
    current = min_prob
    while current <= max_prob + 1e-9:
        values.append(round(current, 3))
        current += step
    return tuple(sorted(set(values)))


@st.cache_data(show_spinner=False)
def run_simulation_cached(config: SimulationConfig) -> pd.DataFrame:
    random.seed(config.random_seed)

    attack_probs = build_attack_probabilities(
        min_prob=config.attack_prob_min,
        max_prob=config.attack_prob_max,
        step=config.attack_prob_step,
    )

    rows: list[dict[str, float | int | bool]] = []

    for n_qubits in sorted(set(config.qubit_counts)):
        for attack_prob in attack_probs:
            eve_present = attack_prob > 0.0
            for trial in range(1, config.n_trials + 1):
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
                        "eve_present": eve_present,
                        "qber": float(result["qber"]),
                        "sifted_length": int(result["sifted_length"]),
                        "sifting_ratio": float(result["sifted_length"]) / float(n_qubits),
                    }
                )

    return pd.DataFrame(rows)


def get_default_config() -> SimulationConfig:
    return SimulationConfig(
        n_trials=12,
        random_seed=42,
        qubit_counts=(500, 1000, 2000),
        attack_prob_min=0.0,
        attack_prob_max=1.0,
        attack_prob_step=0.1,
    )


def get_active_dataframe() -> pd.DataFrame:
    return st.session_state.get("simulation_df", pd.DataFrame())
