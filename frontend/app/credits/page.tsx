"use client";

import { useEffect, useState } from "react";
import { getCredits, createCredit, getDebtors } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";

interface Credit {
  id: number; amount: number; balance_due: number; status: string;
  description: string | null; debtor_id: number; due_date: string | null; created_at: string;
}

interface Debtor { id: number; name: string; }

export default function CreditsPage() {
  const [credits, setCredits] = useState<Credit[]>([]);
  const [debtors, setDebtors] = useState<Debtor[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ debtor_id: 0, amount: "", description: "", due_date: "" });
  const [loading, setLoading] = useState(true);

  const load = () => {
    getCredits().then((res) => setCredits(res.data.items)).catch(() => {}).finally(() => setLoading(false));
    getDebtors({ page_size: 100 }).then((res) => setDebtors(res.data.items)).catch(() => {});
  };

  useEffect(() => {
    if (!isAuthenticated()) { window.location.href = "/login"; return; }
    load();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await createCredit({
      debtor_id: form.debtor_id,
      amount: parseFloat(form.amount),
      description: form.description || undefined,
      due_date: form.due_date || undefined,
    });
    setForm({ debtor_id: 0, amount: "", description: "", due_date: "" });
    setShowForm(false);
    load();
  };

  const statusColor: Record<string, string> = {
    active: "bg-blue-100 text-blue-700",
    paid: "bg-green-100 text-green-700",
    overdue: "bg-red-100 text-red-700",
    written_off: "bg-gray-100 text-gray-500",
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Credits</h1>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? "Cancel" : "+ New Credit"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="card mb-6 space-y-4">
          <select className="input" required value={form.debtor_id}
            onChange={(e) => setForm({ ...form, debtor_id: parseInt(e.target.value) })}>
            <option value={0}>Select Debtor *</option>
            {debtors.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
          <input className="input" placeholder="Amount (₦) *" type="number" required min="0.01" step="0.01"
            value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
          <input className="input" placeholder="Description (optional)"
            value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <input className="input" placeholder="Due Date" type="date"
            value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
          <button type="submit" className="btn-primary" disabled={!form.debtor_id || !form.amount}>
            Create Credit
          </button>
        </form>
      )}

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : credits.length === 0 ? (
        <p className="text-gray-500">No credits yet. Create your first one above.</p>
      ) : (
        <div className="space-y-3">
          {credits.map((c) => (
            <div key={c.id} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">₦{Number(c.amount).toLocaleString("en-NG", { minimumFractionDigits: 2 })}</p>
                  <p className="text-sm text-gray-500">
                    Balance: ₦{Number(c.balance_due).toLocaleString("en-NG", { minimumFractionDigits: 2 })}
                    {c.description && <span> · {c.description}</span>}
                  </p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${statusColor[c.status] || "bg-gray-100"}`}>
                  {c.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
