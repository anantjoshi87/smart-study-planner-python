import { useCallback, useEffect, useMemo, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import AuthPanel from './components/AuthPanel';
import Header from './components/Header';
import ConfigPanel from './components/ConfigPanel';
import HistoryPanel from './components/HistoryPanel';
import ResultsPanel from './components/ResultsPanel';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

function App() {
  const [subjects, setSubjects] = useState([{ name: 'Math', priority: 5 }]);
  const [hoursPerDay, setHoursPerDay] = useState(6);
  const [days, setDays] = useState(3);

  const [token, setToken] = useState(() => localStorage.getItem('studyPlannerToken'));
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('studyPlannerUser');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [authLoading, setAuthLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [saveStatus, setSaveStatus] = useState(null);

  const [originalPlan, setOriginalPlan] = useState(null);
  const [aiPlan, setAiPlan] = useState(null);

  const authHeaders = useMemo(() => (
    token ? { Authorization: `Bearer ${token}` } : {}
  ), [token]);

  const logout = useCallback(() => {
    localStorage.removeItem('studyPlannerToken');
    localStorage.removeItem('studyPlannerUser');
    localStorage.removeItem('studyPlannerData');
    setToken(null);
    setUser(null);
    setHistory([]);
    setOriginalPlan(null);
    setAiPlan(null);
    setSaveStatus(null);
  }, []);

  const loadHistory = useCallback(async () => {
    if (!token) return;
    setHistoryLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/plans`, { headers: authHeaders });
      if (res.status === 401) {
        logout();
        return;
      }
      if (!res.ok) throw new Error('Failed to load history.');
      setHistory(await res.json());
    } catch (err) {
      setError(err.message || 'Failed to load history.');
    } finally {
      setHistoryLoading(false);
    }
  }, [authHeaders, logout, token]);

  useEffect(() => {
    if (!token) return;

    const savedData = localStorage.getItem('studyPlannerData');
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData);
        if (parsed.originalPlan) setOriginalPlan(parsed.originalPlan);
        if (parsed.aiPlan) setAiPlan(parsed.aiPlan);
      } catch (err) {
        console.error('Failed to parse local storage', err);
      }
    }

    loadHistory();
  }, [loadHistory, token]);

  const handleAuth = async (mode, form) => {
    setAuthLoading(true);
    setError(null);
    try {
      const endpoint = mode === 'signup' ? '/auth/register' : '/auth/login';
      const payload = mode === 'signup'
        ? { name: form.name, email: form.email, password: form.password }
        : { email: form.email, password: form.password };

      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Authentication failed.');

      localStorage.setItem('studyPlannerToken', data.access_token);
      localStorage.setItem('studyPlannerUser', JSON.stringify(data.user));
      setToken(data.access_token);
      setUser(data.user);
    } catch (err) {
      setError(err.message || 'Authentication failed.');
    } finally {
      setAuthLoading(false);
    }
  };

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
    const validSubjects = subjects.filter((subject) => subject.name.trim() !== '');
    if (validSubjects.length === 0) {
      setError('Please add at least one valid subject.');
      return;
    }
    setError(null);
    setSaveStatus(null);
    setLoading(true);

    try {
      const payload = {
        subjects: validSubjects,
        hours_per_day: parseFloat(hoursPerDay) || 1,
        days: parseInt(days, 10) || 1,
      };

      const res = await fetch(`${API_BASE_URL}/generate-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders },
        body: JSON.stringify(payload),
      });

      if (res.status === 401) {
        logout();
        throw new Error('Please log in to generate a study plan.');
      }

      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail.detail || 'Failed to generate plan.');
      }

      const data = await res.json();
      setOriginalPlan(data.original_plan);
      setAiPlan(data.ai_plan);
      localStorage.setItem('studyPlannerData', JSON.stringify({
        originalPlan: data.original_plan,
        aiPlan: data.ai_plan,
      }));

      setSaveStatus('saving');
      const subjectNames = validSubjects.map((subject) => subject.name).join(', ');
      const autoTitle = `Plan: ${subjectNames} - ${payload.days} day(s)`;
      const saveRes = await fetch(`${API_BASE_URL}/save-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders },
        body: JSON.stringify({
          title: autoTitle,
          subjects: validSubjects,
          hours_per_day: payload.hours_per_day,
          days: payload.days,
          original_plan: data.original_plan,
          ai_plan: data.ai_plan,
        }),
      });

      if (!saveRes.ok) throw new Error('Plan generated but could not be saved to history.');
      setSaveStatus('saved');
      await loadHistory();
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
      setSaveStatus(err.message?.includes('history') ? 'error' : null);
    } finally {
      setLoading(false);
    }
  };

  const selectPlan = (plan) => {
    setOriginalPlan(plan.original_plan);
    setAiPlan(plan.ai_plan);
    localStorage.setItem('studyPlannerData', JSON.stringify({
      originalPlan: plan.original_plan,
      aiPlan: plan.ai_plan,
    }));
  };

  const deletePlan = async (planId) => {
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/plans/${planId}`, {
        method: 'DELETE',
        headers: authHeaders,
      });
      if (!res.ok) throw new Error('Failed to delete plan.');
      setHistory((current) => current.filter((plan) => plan.id !== planId));
    } catch (err) {
      setError(err.message || 'Failed to delete plan.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6 font-sans text-slate-800 md:p-12">
      <div className="mx-auto max-w-6xl space-y-8">
        <Header user={user} onLogout={logout} />

        {error && (
          <div className="flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700 shadow-sm transition-all">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {!user ? (
          <AuthPanel onSubmit={handleAuth} loading={authLoading} />
        ) : (
          <>
            {saveStatus === 'saving' && (
              <div className="rounded-xl border border-blue-200 bg-blue-50 p-3 text-sm text-blue-700">Saving plan to history...</div>
            )}
            {saveStatus === 'saved' && (
              <div className="rounded-xl border border-green-200 bg-green-50 p-3 text-sm text-green-700">Plan saved to history successfully.</div>
            )}
            {saveStatus === 'error' && (
              <div className="rounded-xl border border-yellow-200 bg-yellow-50 p-3 text-sm text-yellow-700">Plan generated but could not be saved to history.</div>
            )}

            <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
              <div className="space-y-6 lg:col-span-4">
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
                <HistoryPanel
                  plans={history}
                  loading={historyLoading}
                  onSelectPlan={selectPlan}
                  onDeletePlan={deletePlan}
                />
              </div>

              <div className="space-y-6 lg:col-span-8">
                <ResultsPanel originalPlan={originalPlan} aiPlan={aiPlan} loading={loading} />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
