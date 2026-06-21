"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { login } from '@/lib/api';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('password123'); // Default for quick developer testing
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setError(null);
    setLoading(true);

    try {
      // 1. Authenticate with backend and retrieve token
      const authRes = await login(email, password);
      const token = authRes.access_token;
      
      // Save token in localStorage
      localStorage.setItem('auth_token', token);

      // 2. Synchronize user profile with backend to ensure default workspace/project exists
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const syncRes = await fetch(`${apiBase}/workspaces/sync?full_name=Dev%20User&organization_name=Dev%20Organization`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!syncRes.ok) {
        throw new Error(`Sync profile failed: ${syncRes.statusText}`);
      }

      const syncData = await syncRes.json();
      console.log('User synchronization success:', syncData);

      // 3. Redirect to dashboard
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Incorrect email or password. Remember to use "password123" for dev mode.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center px-6 py-12 selection:bg-emerald-500 selection:text-black">
      {/* Brand logo */}
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center font-bold text-black shadow-lg shadow-emerald-500/20 text-lg">
          P
        </div>
        <span className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
          PROFOUND <span className="text-emerald-400 font-medium">GEO</span>
        </span>
      </div>

      {/* Login Card */}
      <div className="w-full max-w-md bg-slate-900/80 p-8 rounded-2xl border border-slate-800 shadow-2xl backdrop-blur-md">
        <h2 className="text-2xl font-bold text-center mb-2">Access GEO Dashboard</h2>
        <p className="text-center text-sm text-slate-400 mb-8">
          Sign in to manage tracking keywords and monitor AI engine visibility.
        </p>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-xs font-semibold tracking-wider text-slate-400 uppercase mb-2">
              Email Address
            </label>
            <input
              type="email"
              placeholder="alex@aether.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full h-11 px-4 rounded-xl border border-slate-800 bg-slate-950 text-white placeholder:text-slate-700 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-sm font-medium"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold tracking-wider text-slate-400 uppercase mb-2">
              Password
            </label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full h-11 px-4 rounded-xl border border-slate-800 bg-slate-950 text-white placeholder:text-slate-700 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-sm font-medium"
            />
          </div>

          {error && (
            <div className="p-3 rounded-xl border border-red-500/20 bg-red-500/5 text-xs text-red-400 font-medium leading-relaxed">
              {error}
            </div>
          )}

          <div className="p-4 rounded-xl border border-emerald-500/10 bg-emerald-500/5 text-xs text-slate-400 space-y-1.5 leading-relaxed">
            <span className="font-bold text-emerald-400">Sandbox Developer Notice:</span>
            <p>
              Use any email and password <code className="text-emerald-300 font-bold">password123</code> to log in. Profile mapping is generated automatically.
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full h-11 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-black hover:from-emerald-400 hover:to-teal-400 transition-all font-semibold tracking-wide shadow-lg shadow-emerald-500/10 cursor-pointer disabled:opacity-50 text-sm"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-8 text-center border-t border-slate-800/80 pt-6">
          <Link href="/" className="text-xs text-emerald-400 hover:underline font-medium">
            ← Return to Public Page Auditor
          </Link>
        </div>
      </div>
    </div>
  );
}
