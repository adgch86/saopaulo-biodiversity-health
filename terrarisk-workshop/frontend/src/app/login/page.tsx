'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function LoginPage() {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const isAdmin = searchParams.get('admin') === 'true';
  const redirect = searchParams.get('redirect') || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password, isAdmin }),
      });

      if (res.ok) {
        router.push(redirect);
        router.refresh();
      } else {
        const data = await res.json();
        setError(data.error || 'Incorrect password');
      }
    } catch {
      setError('Connection error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-risk-bg flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-emerald-500 to-cyan-500 rounded-2xl shadow-lg shadow-emerald-500/20 mb-4">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-risk-text tracking-tight" style={{ fontFamily: 'Instrument Serif, serif' }}>
            TerraRisk
          </h1>
          <p className="text-sm text-risk-muted mt-1" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            {isAdmin ? 'ADMIN ACCESS' : 'PROTECTED PLATFORM'}
          </p>
        </div>

        {/* Login form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="bg-risk-surface border border-[rgba(255,255,255,0.06)] rounded-xl p-6">
            <label className="block text-xs font-medium text-risk-muted uppercase tracking-widest mb-2"
              style={{ fontFamily: 'JetBrains Mono, monospace' }}>
              {isAdmin ? 'Admin Password' : 'Access Password'}
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              className="w-full px-4 py-3 bg-risk-bg border border-[rgba(255,255,255,0.1)] rounded-lg text-risk-text placeholder-risk-dim focus:outline-none focus:border-risk-accent focus:ring-1 focus:ring-risk-accent/30 transition-colors"
              autoFocus
            />

            {error && (
              <p className="mt-3 text-sm text-red-400 flex items-center gap-1.5">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                {error}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading || !password}
            className="w-full py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-medium rounded-lg hover:from-emerald-400 hover:to-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-emerald-500/20"
          >
            {loading ? 'Verifying...' : 'Access Platform'}
          </button>
        </form>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-[10px] text-risk-dim uppercase tracking-widest" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            TERRAX &middot; TERRARISK &middot; 2026
          </p>
          <p className="text-[10px] text-risk-dim mt-1">
            Authorized access only
          </p>
        </div>
      </div>
    </main>
  );
}
