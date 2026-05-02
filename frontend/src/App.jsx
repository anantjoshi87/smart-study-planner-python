import { useState, useEffect } from 'react';
import { AlertCircle } from 'lucide-react';
import Header from './components/Header';
import ConfigPanel from './components/ConfigPanel';
import ResultsPanel from './components/ResultsPanel';

function App() {
  const [subjects, setSubjects] = useState([{ name: 'Math', priority: 5 }]);
  const [hoursPerDay, setHoursPerDay] = useState(6);
  const [days, setDays] = useState(3);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [originalPlan, setOriginalPlan] = useState(null);
  const [aiPlan, setAiPlan] = useState(null);
  const [history, setHistory] = useState([]);

  // Fetch all history from the database
  const fetchHistory = async () => {
    try {
      const res = await fetch("http://localhost:8000/history/1");
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error("Error fetching history:", err);
    }
  };

  // Load history on startup
  useEffect(() => {
    fetchHistory();
  }, []);

  // Sync with local storage for persistence on refresh (Optional)
  useEffect(() => {
    const savedData = localStorage.getItem('studyPlannerData');
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData);
        if (parsed.originalPlan) setOriginalPlan(parsed.originalPlan);
        if (parsed.aiPlan) setAiPlan(parsed.aiPlan);
      } catch (e) {
        console.error("Failed to parse local storage", e);
      }
    }
  }, []);

  const addSubject = () => {
    setSubjects([...subjects, { name: '', priority: 3 }]);
  };

  const removeSubject = (index) => {
    setSubjects(subjects.filter((_, i) => i !== index));
  };

  const updateSubject = (index, field, value) => {
    const newSubjects = [...subjects];
    if (field === 'priority' && value) {
      value = parseInt(value, 10);
      if (value < 1) value = 1;
      if (value > 5) value = 5;
    }
    newSubjects[index][field] = value;
    setSubjects(newSubjects);
  };

  const generatePlan = async () => {
    const validSubjects = subjects.filter((s) => s.name.trim() !== '');
    if (validSubjects.length === 0) {
      setError("Please add at least one valid subject.");
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const payload = {
        user_id: 1,
        subjects: validSubjects,
        hours_per_day: parseFloat(hoursPerDay) || 1,
        days: parseInt(days, 10) || 1,
      };

      const res = await fetch("http://localhost:8000/generate-plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        let errDesc = "Failed to generate plan.";
        try {
          const detail = await res.json();
          errDesc = detail.detail || errDesc;
        } catch (e) {}
        throw new Error(errDesc);
      }

      const data = await res.json();
      setOriginalPlan(data.original_plan);
      setAiPlan(data.ai_plan);

      console.log("Plan saved to MySQL. Session ID:", data.session_id);

      // Refresh history list immediately
      fetchHistory();
    } catch (err) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-12 font-sans text-slate-800">
      <div className="max-w-6xl mx-auto space-y-8">
        <Header />

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-center gap-3 shadow-sm transition-all">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p>{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* LEFT: Configuration Panel */}
          <div className="lg:col-span-4 space-y-6">
            <ConfigPanel
              hoursPerDay={hoursPerDay}
              setHoursPerDay={setHoursPerDay}
              days={days}
              setDays={setDays}
              subjects={subjects}
              updateSubject={updateSubject}
              removeSubject={removeSubject}
              addSubject={addSubject}
              generatePlan={generatePlan}
              loading={loading}
            />
          </div>

          {/* RIGHT: Results Display */}
          <div className="lg:col-span-8 space-y-6">
            <ResultsPanel
              originalPlan={originalPlan}
              aiPlan={aiPlan}
              loading={loading}
            />
            
            {/* HISTORY SECTION (Integrated inside the layout) */}
            <div className="bg-white p-6 rounded-2xl shadow-lg border border-slate-200">
              <h2 className="text-2xl font-bold mb-6 text-slate-800">Study History</h2>
              <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                {history.length === 0 ? (
                  <p className="text-slate-400 italic">No previous plans found.</p>
                ) : (
                  history.map((item) => (
                    <div key={item.id} className="p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-blue-300 transition-all">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-xs font-semibold text-blue-600 uppercase tracking-wider">
                            {new Date(item.created_at).toLocaleDateString()}
                          </p>
                          <h3 className="font-bold text-slate-800 mt-1">
                            {item.hours_per_day}h/day • {item.total_days} Days
                          </h3>
                        </div>
                        <button
                          onClick={() => {
                            setAiPlan(item.raw_ai_json);
                            window.scrollTo({ top: 0, behavior: 'smooth' });
                          }}
                          className="text-xs bg-white border border-slate-300 px-3 py-1.5 rounded-lg hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 transition-colors shadow-sm"
                        >
                          View Details
                        </button>
                      </div>

                      <div className="flex gap-2 mt-3 flex-wrap">
                        {item.subjects?.map((sub, i) => (
                          <span key={i} className="text-[10px] bg-white border border-slate-200 text-slate-600 px-2 py-0.5 rounded-md shadow-xs">
                            {sub.subject_name}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
