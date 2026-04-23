import { Plus, Trash2, Loader2, Sparkles } from 'lucide-react';

export default function ConfigPanel({
  hoursPerDay, setHoursPerDay,
  days, setDays,
  subjects, updateSubject, removeSubject, addSubject,
  generatePlan, loading
}) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="text-sm font-semibold text-slate-600 block">Hours / Day</label>
          <input 
            type="number" min="1" max="24"
            value={hoursPerDay} onChange={(e) => setHoursPerDay(e.target.value)}
            className="w-full border border-slate-200 rounded-lg p-3 text-slate-700 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all outline-none"
          />
        </div>
        <div className="space-y-1">
          <label className="text-sm font-semibold text-slate-600 block">Total Days</label>
          <input 
            type="number" min="1" max="365"
            value={days} onChange={(e) => setDays(e.target.value)}
            className="w-full border border-slate-200 rounded-lg p-3 text-slate-700 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all outline-none"
          />
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <label className="text-sm font-semibold text-slate-600">Subjects & Priorities</label>
        </div>
        
        <div className="space-y-3">
          {subjects.map((sub, index) => (
            <div key={index} className="flex items-center gap-2 bg-slate-50 p-2 rounded-lg border border-slate-100">
              <input 
                type="text" placeholder="Subject Name"
                value={sub.name} onChange={(e) => updateSubject(index, 'name', e.target.value)}
                className="flex-1 min-w-0 bg-white border border-slate-200 rounded-md p-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
              />
              <select 
                value={sub.priority} onChange={(e) => updateSubject(index, 'priority', e.target.value)}
                className="bg-white border border-slate-200 rounded-md p-2 text-sm cursor-pointer focus:ring-2 focus:ring-indigo-500 outline-none"
              >
                <option value="1">1 (Low)</option>
                <option value="2">2</option>
                <option value="3">3 (Med)</option>
                <option value="4">4</option>
                <option value="5">5 (High)</option>
              </select>
              <button 
                onClick={() => removeSubject(index)}
                className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors"
                title="Remove Subject"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>

        <button 
          onClick={addSubject}
          className="mt-3 w-full border-2 border-dashed border-slate-200 text-slate-500 hover:border-indigo-400 hover:text-indigo-500 rounded-lg p-3 flex items-center justify-center gap-2 text-sm font-medium transition-all"
        >
          <Plus className="w-4 h-4" /> Add Subject
        </button>
      </div>

      <button 
        onClick={generatePlan}
        disabled={loading}
        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold flex items-center justify-center gap-2 py-4 rounded-xl shadow-md disabled:opacity-70 disabled:cursor-not-allowed transition-all"
      >
        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
        {loading ? "Optimizing & Generating..." : "Generate AI Plan"}
      </button>
    </div>
  );
}
