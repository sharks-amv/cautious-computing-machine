'use client';

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  BarChart,
  Bar
} from 'recharts';
import { motion } from 'framer-motion';
import { SweepPoint, SimulationResponse } from '../lib/types';

type Props = {
  lineData: SweepPoint[];
  simulation: SimulationResponse | null;
};

export default function ChartsPanel({ lineData, simulation }: Props) {
  const histogramData = simulation
    ? simulation.distribution.map((qber, idx) => ({ bin: idx + 1, qber }))
    : [];

  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="card"
      >
        <h3 className="mb-4 text-sm font-semibold text-slate-700">QBER vs Attack Probability</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={lineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="attack_probability" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="avg_qber" stroke="#0F172A" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="card"
      >
        <h3 className="mb-4 text-sm font-semibold text-slate-700">QBER Distribution</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={histogramData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="bin" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="qber" fill="#334155" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>
    </div>
  );
}
