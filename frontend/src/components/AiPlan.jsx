export default function AiPlan({ aiPlan }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
      <div className="bg-indigo-50 border-b border-indigo-100 p-4">
        <h2 className="text-indigo-800 font-bold text-lg flex items-center gap-2">
           ✨ AI Enhanced Schedule
        </h2>
        <p className="text-sm text-indigo-600 opacity-80 mt-1 truncate">
            Smarter breaks, burnout prevention
        </p>
      </div>
      <div className="p-5 flex-1 overflow-auto max-h-[600px]">
        <div className="prose prose-sm prose-indigo max-w-none whitespace-pre-wrap leading-relaxed text-slate-700">
            {aiPlan ? aiPlan : (
                <div className="text-slate-400 italic">No AI Plan generated.</div>
            )}
        </div>
      </div>
    </div>
  );
}
