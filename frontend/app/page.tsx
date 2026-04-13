'use client';

import { motion } from 'framer-motion';
import { useMemo, useState } from 'react';
import ChartsPanel from '../components/ChartsPanel';
import KpiCards from '../components/KpiCards';
import Sidebar from '../components/Sidebar';
import { simulate } from '../lib/api';
import { SimulationResponse, SweepPoint } from '../lib/types';

function buildSweep(maxAttack: number): number[] {
  const values: number[] = [];
  for (let p = 0; p <= maxAttack + 1e-9; p += 0.1) values.push(Number(p.toFixed(1)));
  return Array.from(new Set(values));
}

export default function Page() {
  const [qubits, setQubits] = useState(1000);
  const [attackMax, setAttackMax] = useState(1.0);
  const [trials, setTrials] = useState(20);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [simulation, setSimulation] = useState<SimulationResponse | null>(null);
  const [lineData, setLineData] = useState<SweepPoint[]>([]);

  const canRender = useMemo(() => simulation !== null && lineData.length > 0, [simulation, lineData]);

  async function onRun() {
    setRunning(true);
    setError(null);

    try {
      const attacks = buildSweep(attackMax);
      const series: SweepPoint[] = [];

      for (const p of attacks) {
        const result = await simulate(qubits, p, trials);
        series.push({ attack_probability: p, avg_qber: result.avg_qber });
        if (p === attacks[attacks.length - 1]) {
          setSimulation(result);
        }
      }

      setLineData(series);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setRunning(false);
    }
  }

  return (
    <main className="min-h-screen p-6 lg:p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">BB84 Dashboard</h1>
        <p className="mt-1 text-sm text-slate-600">Next.js analytics interface powered by FastAPI simulations</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="lg:col-span-3">
          <Sidebar
            qubits={qubits}
            setQubits={setQubits}
            attackMax={attackMax}
            setAttackMax={setAttackMax}
            trials={trials}
            setTrials={setTrials}
            running={running}
            onRun={onRun}
          />
        </div>

        <div className="space-y-6 lg:col-span-9">
          {running && (
            <motion.div
              className="card"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <div className="h-2 w-full overflow-hidden rounded bg-slate-200">
                <motion.div
                  className="h-full bg-slate-800"
                  initial={{ x: '-100%' }}
                  animate={{ x: '100%' }}
                  transition={{ repeat: Infinity, duration: 1.2, ease: 'linear' }}
                />
              </div>
              <p className="mt-3 text-sm text-slate-600">Running simulations...</p>
            </motion.div>
          )}

          {error && <div className="card border-red-200 text-sm text-red-700">{error}</div>}

          {canRender && simulation && (
            <>
              <KpiCards
                avgQber={simulation.avg_qber}
                maxQber={simulation.max_qber}
                avgSiftedLength={simulation.avg_sifted_length}
              />
              <ChartsPanel lineData={lineData} simulation={simulation} />
            </>
          )}

          {!running && !canRender && !error && (
            <div className="card text-sm text-slate-600">Configure parameters and run a simulation.</div>
          )}
        </div>
      </div>
    </main>
  );
}
