import { Clock, Trash2 } from 'lucide-react';

export default function HistoryPanel({ plans, loading, onSelectPlan, onDeletePlan }) {
  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="flex items-center gap-2 text-lg font-bold text-slate-800">
          <Clock className="h-5 w-5 text-indigo-500" /> History
        </h2>
        <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-500">
          {plans.length}
        </span>
      </div>

      {loading ? (
        <p className="text-sm text-slate-400">Loading saved plans...</p>
      ) : plans.length === 0 ? (
        <p className="text-sm text-slate-400">Generated plans will appear here after they are saved.</p>
      ) : (
        <div className="space-y-2">
          {plans.map((plan) => (
            <div key={plan.id} className="rounded-xl border border-slate-100 bg-slate-50 p-3">
              <button
                type="button"
                onClick={() => onSelectPlan(plan)}
                className="block w-full text-left"
              >
                <span className="block truncate text-sm font-semibold text-slate-700">{plan.title}</span>
                <span className="mt-1 block text-xs text-slate-400">
                  {new Date(plan.created_at).toLocaleString()} | {plan.days} day(s)
                </span>
              </button>
              <button
                type="button"
                onClick={() => onDeletePlan(plan.id)}
                className="mt-2 inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs font-semibold text-red-500 hover:bg-red-50"
              >
                <Trash2 className="h-3.5 w-3.5" /> Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
