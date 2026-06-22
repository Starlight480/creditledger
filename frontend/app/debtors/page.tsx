"use client";

import { useEffect, useState } from "react";
import { getDebtors, createDebtor } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";

interface Debtor {
  id: number; name: string; phone: string | null; email: string | null;
  address: string | null; is_active: boolean; created_at: string;
}

export default function DebtorsPage() {
  const [debtors, setDebtors] = useState<Debtor[]>([]);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", phone: "", email: "", address: "", notes: "" });
  const [loading, setLoading] = useState(true);

  const load = () => {
    getDebtors({ search: search || undefined })
      .then((res) => setDebtors(res.data.items))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (!isAuthenticated()) { window.location.href = "/login"; return; }
    load();
  }, [search]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await createDebtor(form);
    setForm({ name: "", phone: "", email: "", address: "", notes: "" });
    setShowForm(false);
    load();
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Debtors</h1>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? "Cancel" : "+ Add Debtor"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="card mb-6 space-y-4">
          <input className="input" placeholder="Name *" required
            value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <div className="grid grid-cols-2 gap-4">
            <input className="input" placeholder="Phone" value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            <input className="input" placeholder="Email" value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>
          <input className="input" placeholder="Address" value={form.address}
            onChange={(e) => setForm({ ...form, address: e.target.value })} />
          <button type="submit" className="btn-primary">Save Debtor</button>
        </form>
      )}

      <input className="input mb-4" placeholder="Search debtors..."
        value={search} onChange={(e) => setSearch(e.target.value)} />

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : debtors.length === 0 ? (
        <p className="text-gray-500">No debtors yet. Add your first one above.</p>
      ) : (
        <div className="space-y-3">
          {debtors.map((d) => (
            <div key={d.id} className="card flex items-center justify-between">
              <div>
                <p className="font-medium">{d.name}</p>
                <p className="text-sm text-gray-500">
                  {d.phone && <span>{d.phone}</span>}
                  {d.phone && d.email && <span> · </span>}
                  {d.email && <span>{d.email}</span>}
                </p>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full ${d.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                {d.is_active ? "Active" : "Inactive"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
