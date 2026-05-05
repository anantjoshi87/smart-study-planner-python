import { useState } from 'react';
import { LogIn, UserPlus } from 'lucide-react';

export default function AuthPanel({ onSubmit, loading }) {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ name: '', email: '', password: '' });

  const isSignup = mode === 'signup';

  const updateField = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const submit = (event) => {
    event.preventDefault();
    onSubmit(mode, form);
  };

  return (
    <div className="mx-auto max-w-md rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
      <div className="mb-6 flex rounded-xl bg-slate-100 p-1">
        <button
          type="button"
          onClick={() => setMode('login')}
          className={`flex-1 rounded-lg px-4 py-2 text-sm font-semibold transition-colors ${!isSignup ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
        >
          Log in
        </button>
        <button
          type="button"
          onClick={() => setMode('signup')}
          className={`flex-1 rounded-lg px-4 py-2 text-sm font-semibold transition-colors ${isSignup ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
        >
          Sign up
        </button>
      </div>

      <form onSubmit={submit} className="space-y-4">
        {isSignup && (
          <div className="space-y-1">
            <label className="block text-sm font-semibold text-slate-600">Name</label>
            <input
              type="text"
              required
              minLength={2}
              value={form.name}
              onChange={(event) => updateField('name', event.target.value)}
              className="w-full rounded-lg border border-slate-200 p-3 text-slate-700 outline-none transition-all focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        )}

        <div className="space-y-1">
          <label className="block text-sm font-semibold text-slate-600">Email</label>
          <input
            type="email"
            required
            value={form.email}
            onChange={(event) => updateField('email', event.target.value)}
            className="w-full rounded-lg border border-slate-200 p-3 text-slate-700 outline-none transition-all focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="space-y-1">
          <label className="block text-sm font-semibold text-slate-600">Password</label>
          <input
            type="password"
            required
            minLength={6}
            value={form.password}
            onChange={(event) => updateField('password', event.target.value)}
            className="w-full rounded-lg border border-slate-200 p-3 text-slate-700 outline-none transition-all focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 py-3 font-semibold text-white shadow-md transition-all hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isSignup ? <UserPlus className="h-5 w-5" /> : <LogIn className="h-5 w-5" />}
          {loading ? 'Please wait...' : isSignup ? 'Create account' : 'Log in'}
        </button>
      </form>
    </div>
  );
}
