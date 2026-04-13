from __future__ import annotations

from statistics import mean

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    qubits: int = Field(..., ge=1, le=100_000)
    attack_probability: float = Field(..., ge=0.0, le=1.0)
    trials: int = Field(..., ge=1, le=500)


class SimulationResponse(BaseModel):
    qubits: int
    attack_probability: float
    trials: int
    avg_qber: float
    max_qber: float
    avg_sifted_length: float
    points: list[dict[str, float | int]]
    distribution: list[float]


app = FastAPI(title="BB84 Simulation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/simulate", response_model=SimulationResponse)
def simulate(payload: SimulationRequest) -> SimulationResponse:
    try:
        from bb84_simulation import simulate_bb84
    except Exception as exc:  # dependency/import/runtime environment issue
        raise HTTPException(status_code=500, detail=f"Simulation import failed: {exc}") from exc

    trial_points: list[dict[str, float | int]] = []
    qbers: list[float] = []
    sifted_lengths: list[int] = []

    for trial in range(1, payload.trials + 1):
        result = simulate_bb84(
            n_qubits=payload.qubits,
            eve_present=payload.attack_probability > 0.0,
            eve_attack_prob=payload.attack_probability,
        )
        qber = float(result["qber"])
        sifted = int(result["sifted_length"])

        qbers.append(qber)
        sifted_lengths.append(sifted)
        trial_points.append(
            {
                "trial": trial,
                "qber": qber,
                "sifted_length": sifted,
            }
        )

    return SimulationResponse(
        qubits=payload.qubits,
        attack_probability=payload.attack_probability,
        trials=payload.trials,
        avg_qber=mean(qbers),
        max_qber=max(qbers),
        avg_sifted_length=mean(sifted_lengths),
        points=trial_points,
        distribution=qbers,
    )
