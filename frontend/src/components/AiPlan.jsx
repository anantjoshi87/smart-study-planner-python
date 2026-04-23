export default function AiPlan({ aiPlan }) {
  let isError = false;
  let displayText = aiPlan;

  if (aiPlan && typeof aiPlan === 'object') {
    isError = true;
    displayText = aiPlan.message || JSON.stringify(aiPlan);
  } else if (aiPlan && typeof aiPlan === 'string') {
    isError = aiPlan.toLowerCase().includes("failed") || aiPlan.toLowerCase().includes("busy");
  }

  return (
    <div className={`bg-white rounded-2xl shadow-sm border ${isError ? 'border-red-200' : 'border-slate-100'} overflow-hidden flex flex-col`}>
      <div className={`${isError ? 'bg-red-50 border-red-100' : 'bg-indigo-50 border-indigo-100'} border-b p-4`}>
        <h2 className={`${isError ? 'text-red-800' : 'text-indigo-800'} font-bold text-lg flex items-center gap-2`}>
           {isError ? '⚠️ AI Notice' : '✨ AI Enhanced Schedule'}
        </h2>
        <p className={`text-sm ${isError ? 'text-red-600' : 'text-indigo-600'} opacity-80 mt-1 truncate`}>
            {isError ? 'Temporary issue with AI' : 'Smarter breaks, burnout prevention'}
        </p>
      </div>
      <div className="p-5 flex-1 overflow-auto max-h-[600px]">
        <div className={`prose prose-sm ${isError ? 'prose-red' : 'prose-indigo'} max-w-none whitespace-pre-wrap leading-relaxed ${isError ? 'text-red-700 font-medium' : 'text-slate-700'}`}>
            {displayText ? displayText : (
                <div className="text-slate-400 italic">No AI Plan generated.</div>
            )}
        </div>
      </div>
    </div>
  );
}
