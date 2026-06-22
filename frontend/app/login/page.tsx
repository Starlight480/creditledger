"use client";

import { useState } from "react";
import { login, register } from "@/lib/api";
import { setTokens } from "@/lib/auth";

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({
    email: "", password: "", full_name: "", business_name: "", phone: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = isRegister
        ? await register(form)
        : await login({ email: form.email, password: form.password });
      setTokens(res.data.access_token, res.data.refresh_token);
      window.location.href = "/";
    } catch (err: any) {
      setError(err.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="card w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">
          {isRegister ? "Create Account" : "Welcome Back"}
        </h1>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <>
              <input className="input" placeholder="Business Name" required
                value={form.business_name} onChange={(e) => setForm({ ...form, business_name: e.target.value })} />
              <input className="input" placeholder="Your Full Name" required
                value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
              <input className="input" placeholder="Phone (optional)" type="tel"
                value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </>
          )}
          <input className="input" placeholder="Email" type="email" required
            value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="input" placeholder="Password" type="password" required minLength={8}
            value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />

          <button type="submit" className="btn-primary w-full" disabled={loading}>
            {loading ? "Please wait..." : isRegister ? "Create Account" : "Sign In"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          {isRegister ? "Already have an account?" : "Don't have an account?"}{" "}
          <button onClick={() => setIsRegister(!isRegister)} className="text-primary-600 font-medium">
            {isRegister ? "Sign In" : "Create one"}
          </button>
        </p>
      </div>
    </div>
  );
}
