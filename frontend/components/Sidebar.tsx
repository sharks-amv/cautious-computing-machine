'use client';

type Props = {
  qubits: number;
  setQubits: (v: number) => void;
  attackMax: number;
  setAttackMax: (v: number) => void;
  trials: number;
  setTrials: (v: number) => void;
  running: boolean;
  onRun: () => void;
};

export default function Sidebar(props: Props) {
  const { qubits, setQubits, attackMax, setAttackMax, trials, setTrials, running, onRun } = props;

  return (
    <aside className="card h-fit space-y-4">
      <h2 className="text-sm font-semibold tracking-wide text-slate-700">Simulation Controls</h2>

      <label className="block">
        <span className="text-xs text-slate-600">Qubits</span>
        <input
          type="number"
          min={1}
          value={qubits}
          onChange={(e) => setQubits(Number(e.target.value || 1))}
          className="mt-1 w-full rounded-md border border-border px-3 py-2 text-sm"
        />
      </label>

      <label className="block">
        <span className="text-xs text-slate-600">Max attack probability</span>
        <input
          type="range"
          min={0}
          max={1}
          step={0.1}
          value={attackMax}
          onChange={(e) => setAttackMax(Number(e.target.value))}
          className="mt-2 w-full"
        />
        <div className="text-xs text-slate-500">0.0 to {attackMax.toFixed(1)}</div>
      </label>

      <label className="block">
        <span className="text-xs text-slate-600">Trials</span>
        <input
          type="number"
          min={1}
          max={300}
          value={trials}
          onChange={(e) => setTrials(Number(e.target.value || 1))}
          className="mt-1 w-full rounded-md border border-border px-3 py-2 text-sm"
        />
      </label>

      <button
        onClick={onRun}
        disabled={running}
        className="w-full rounded-md bg-slate-900 px-4 py-2 text-sm text-white disabled:opacity-50"
      >
        {running ? 'Running...' : 'Run Simulation'}
      </button>
    </aside>
  );
}
