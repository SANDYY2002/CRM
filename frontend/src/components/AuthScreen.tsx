import { FormEvent, useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Building2, LockKeyhole, Mail, UserRound } from 'lucide-react';
import { api } from '../lib/api';
import { useAuthStore } from '../store/auth';

export function AuthScreen() {
  const setSession = useAuthStore((state) => state.setSession);
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ username: '', password: '', email: '', first_name: '', last_name: '', organization_name: '' });

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (mode === 'login') {
        const result = await api.login({ username: form.username, password: form.password });
        setSession(result.user, result.organizations, result.access, result.refresh);
      } else {
        const result = await api.register(form);
        setSession(result.user, [result.organization], result.access, result.refresh, result.organization.id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to continue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-shell">
      <div className="orb orb-one" /><div className="orb orb-two" />
      <motion.section className="auth-card glass-card" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
        <div className="brand auth-brand"><span className="brand-mark">C</span><span>CRM</span></div>
        <p className="eyebrow">OMNICHANNEL CUSTOMER PLATFORM</p>
        <h1>{mode === 'login' ? 'Welcome back.' : 'Build your workspace.'}</h1>
        <p className="muted">{mode === 'login' ? 'Sign in to manage every customer conversation from one beautiful inbox.' : 'Create your CRM workspace and start connecting customer channels.'}</p>
        <form onSubmit={submit} className="auth-form">
          {mode === 'register' && <>
            <label><UserRound size={16} />Name<input required value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} placeholder="Your name" /></label>
            <label><Building2 size={16} />Workspace<input required value={form.organization_name} onChange={(e) => setForm({ ...form, organization_name: e.target.value })} placeholder="Acme Business" /></label>
            <label><Mail size={16} />Email<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="you@company.com" /></label>
          </>}
          <label><UserRound size={16} />Username<input required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder="sandesh" autoComplete="username" /></label>
          <label><LockKeyhole size={16} />Password<input required minLength={8} type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="••••••••" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} /></label>
          {error && <div className="form-error">{error}</div>}
          <button className="primary-button auth-submit" disabled={loading}>{loading ? 'Please wait…' : mode === 'login' ? 'Enter workspace' : 'Create workspace'} <ArrowRight size={17} /></button>
        </form>
        <button className="auth-switch" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}>{mode === 'login' ? 'Need a workspace? Create one' : 'Already have an account? Sign in'}</button>
      </motion.section>
    </main>
  );
}
