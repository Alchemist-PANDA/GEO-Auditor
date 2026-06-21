"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { register, login } from '@/lib/api';

export default function RegisterPage() {
  const [fullName, setFullName] = useState('');
  const [orgName, setOrgName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !orgName || !email || !password) return;

    setError(null);
    setLoading(true);

    try {
      // 1. Call registration endpoint
      await register(email, password, fullName, orgName);

      // 2. Automatically authenticate with backend to retrieve token
      const authRes = await login(email, password);
      const token = authRes.access_token;
      
      // Save token in localStorage
      localStorage.setItem('auth_token', token);

      // 3. Synchronize user profile to create default workspace/projects
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const syncRes = await fetch(`${apiBase}/workspaces/sync?full_name=${encodeURIComponent(fullName)}&organization_name=${encodeURIComponent(orgName)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!syncRes.ok) {
        throw new Error(`Sync profile failed: ${syncRes.statusText}`);
      }

      // 4. Redirect to dashboard setup
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
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

      {/* Register Card */}
      <div className="w-full max-w-md bg-slate-900/80 p-8 rounded-2xl border border-slate-800 shadow-2xl backdrop-blur-md">
        <h2 className="text-2xl font-bold text-center mb-2 font-sans tracking-tight text-white">Create your account</h2>
        <p className="text-center text-sm text-slate-400 mb-8">
          Get started with real-time generative engine analytics.
        </p>

        <form onSubmit={handleRegister} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold tracking-wider text-slate-400 uppercase mb-2">
              Full Name
            </label>
            <input
              type="text"
              placeholder="Alex Mercer"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              className="w-full h-11 px-4 rounded-xl border border-slate-800 bg-slate-950 text-white placeholder:text-slate-700 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-sm font-medium"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold tracking-wider text-slate-400 uppercase mb-2">
              Company Name
            </label>
            <input
              type="text"
              placeholder="Aether Industries"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              required
              className="w-full h-11 px-4 rounded-xl border border-slate-800 bg-slate-950 text-white placeholder:text-slate-700 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-sm font-medium"
            />
          </div>

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

          <button
            type="submit"
            disabled={loading}
            className="w-full h-11 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-black hover:from-emerald-400 hover:to-teal-400 transition-all font-semibold tracking-wide shadow-lg shadow-emerald-500/10 cursor-pointer disabled:opacity-50 text-sm mt-2"
          >
            {loading ? 'Registering...' : 'Create Account'}
          </button>
        </form>

        <div className="mt-8 text-center border-t border-slate-800/80 pt-6 flex flex-col gap-2">
          <span className="text-xs text-slate-400">
            Already have an account?{' '}
            <Link href="/login" className="text-emerald-400 hover:underline font-medium">
              Sign In
            </Link>
          </span>
          <Link href="/" className="text-xs text-slate-500 hover:underline">
            ← Return to Public Page Auditor
          </Link>
        </div>
      </div>
    </div>
  );
}
