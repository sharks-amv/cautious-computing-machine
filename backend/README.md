# Backend (FastAPI)

## Run
```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

## Endpoint
- `POST /simulate`
  - body:
    - `qubits` (int)
    - `attack_probability` (float 0..1)
    - `trials` (int)

This backend reuses `simulate_bb84()` from `bb84_simulation.py`.
