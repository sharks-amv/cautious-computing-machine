import { SimulationResponse } from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export async function simulate(
  qubits: number,
  attackProbability: number,
  trials: number
): Promise<SimulationResponse> {
  const res = await fetch(`${BASE_URL}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      qubits,
      attack_probability: attackProbability,
      trials
    })
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || 'Simulation request failed');
  }

  return res.json();
}
