export type SimulationPoint = {
  trial: number;
  qber: number;
  sifted_length: number;
};

export type SimulationResponse = {
  qubits: number;
  attack_probability: number;
  trials: number;
  avg_qber: number;
  max_qber: number;
  avg_sifted_length: number;
  points: SimulationPoint[];
  distribution: number[];
};

export type SweepPoint = {
  attack_probability: number;
  avg_qber: number;
};
