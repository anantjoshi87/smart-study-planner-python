export default function GreedyPlan({ originalPlan }) {
  if (!originalPlan) return null;

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
      <div className="bg-emerald-50 border-b border-emerald-100 p-4">
        <h2 className="text-emerald-800 font-bold text-lg flex items-center gap-2">
           📊 Base Allocation
        </h2>
        <p className="text-sm text-emerald-600 opacity-80 mt-1 truncate">
            Strictly math-based proportional allocation
        </p>
      </div>
      <div className="p-5 flex-1 overflow-auto bg-slate-50">
        <div className="bg-white rounded-lg p-4 border border-slate-100 space-y-4 shadow-sm mb-4">
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="bg-slate-50 rounded-md p-3">
                <span className="block text-slate-400 text-xs uppercase font-bold tracking-wider mb-1">Daily Cap</span>
                <span className="font-semibold text-slate-700 text-lg">{originalPlan.metadata.total_daily_hours} hrs</span>
            </div>
            <div className="bg-slate-50 rounded-md p-3">
                <span className="block text-slate-400 text-xs uppercase font-bold tracking-wider mb-1">Timeframe</span>
                <span className="font-semibold text-slate-700 text-lg">{originalPlan.metadata.total_days} days</span>
            </div>
          </div>
        </div>

        <div className="space-y-2">
            {Object.entries(originalPlan.daily_allocation || {}).map(([subject, hours]) => (
                <div key={subject} className="flex items-center justify-between bg-white rounded-lg p-3 border border-slate-100 shadow-sm">
                    <span className="font-medium text-slate-700">{subject}</span>
                    <span className="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full text-sm font-semibold">
                        {hours} hrs / day
                    </span>
                </div>
            ))}
        </div>
      </div>
    </div>
  );
}
