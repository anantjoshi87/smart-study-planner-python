import { LogOut, Sparkles } from 'lucide-react';

export default function Header({ user, onLogout }) {
  return (
    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div className="space-y-2 text-center md:text-left">
        <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-indigo-600 flex items-center justify-center md:justify-start gap-3">
          <Sparkles className="w-9 h-9 md:w-10 md:h-10" /> AI Smart Study Planner
        </h1>
        <p className="text-slate-500 text-base md:text-lg">Generate mathematically optimized, AI-enhanced study schedules.</p>
      </div>

      {user && (
        <div className="flex items-center justify-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
          <div className="min-w-0 text-right">
            <p className="truncate text-sm font-semibold text-slate-700">{user.name}</p>
            <p className="truncate text-xs text-slate-400">{user.email}</p>
          </div>
          <button
            onClick={onLogout}
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800 transition-colors"
            title="Log out"
          >
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      )}
    </div>
  );
}
