import { Sparkles } from 'lucide-react';
import GreedyPlan from './GreedyPlan';
import AiPlan from './AiPlan';

export default function ResultsPanel({ originalPlan, aiPlan, loading }) {
  if (!originalPlan && !loading) {
    return (
      <div className="h-full bg-white rounded-2xl border border-slate-100 flex flex-col items-center justify-center p-12 text-slate-400 min-h-[400px]">
        <Sparkles className="w-16 h-16 text-slate-200 mb-4" />
        <p className="text-lg">Fill out the subjects and generate a plan!</p>
      </div>
    );
  }

  if (originalPlan) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <GreedyPlan originalPlan={originalPlan} />
        <AiPlan aiPlan={aiPlan} />
      </div>
    );
  }

  return null;
}
