import { Sparkles } from 'lucide-react';

export default function Header() {
  return (
    <div className="text-center space-y-2">
      <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-indigo-600 flex items-center justify-center gap-3">
        <Sparkles className="w-10 h-10" /> AI Smart Study Planner
      </h1>
      <p className="text-slate-500 text-lg">Generate mathematically optimized, AI-enhanced study schedules.</p>
    </div>
  );
}
