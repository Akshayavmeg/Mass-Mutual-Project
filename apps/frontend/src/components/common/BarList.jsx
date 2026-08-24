/** Minimal dependency-free horizontal bar chart -- avoids pulling in a
 * charting library for a handful of dashboard bars. */
export function BarList({ items, colorClass = "bg-slate-600" }) {
  const max = Math.max(1, ...items.map((i) => i.value));
  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-3 text-sm">
          <span className="w-28 shrink-0 text-slate-600">{item.label}</span>
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
            <div
              className={`h-full rounded-full ${item.colorClass || colorClass}`}
              style={{ width: `${(item.value / max) * 100}%` }}
            />
          </div>
          <span className="w-10 shrink-0 text-right font-medium text-slate-900">{item.value}</span>
        </div>
      ))}
    </div>
  );
}
