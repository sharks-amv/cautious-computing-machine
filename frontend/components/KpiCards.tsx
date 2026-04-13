'use client';

type Props = {
  avgQber: number;
  maxQber: number;
  avgSiftedLength: number;
};

function Card({ title, value }: { title: string; value: string }) {
  return (
    <div className="card">
      <div className="text-xs text-slate-500">{title}</div>
      <div className="mt-2 text-2xl font-semibold text-slate-900">{value}</div>
    </div>
  );
}

export default function KpiCards({ avgQber, maxQber, avgSiftedLength }: Props) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <Card title="Average QBER" value={`${(avgQber * 100).toFixed(2)}%`} />
      <Card title="Maximum QBER" value={`${(maxQber * 100).toFixed(2)}%`} />
      <Card title="Average Sifted Length" value={`${avgSiftedLength.toFixed(1)} bits`} />
    </div>
  );
}
