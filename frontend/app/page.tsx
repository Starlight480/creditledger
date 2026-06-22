"use client";

import { useEffect, useState } from "react";
import { getSummary } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";

interface SummaryData {
  total_credits: number;
  total_amount_disbursed: number;
  total_outstanding: number;
  total_collected: number;
  overdue_count: number;
  overdue_amount: number;
  active_debtors: number;
}

export default function Dashboard() {
  const [data, setData] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      window.location.href = "/login";
      return;
    }
    getSummary()
      .then((res) => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-screen">Loading...</div>;

  const fmt = (n: number) => "₦" + Number(n).toLocaleString("en-NG", { minimumFractionDigits: 2 });

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="card">
          <p className="text-sm text-gray-500">Total Disbursed</p>
          <p className="text-2xl font-bold text-primary-600">{fmt(data?.total_amount_disbursed || 0)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Outstanding</p>
          <p className="text-2xl font-bold text-orange-600">{fmt(data?.total_outstanding || 0)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Collected</p>
          <p className="text-2xl font-bold text-green-600">{fmt(data?.total_collected || 0)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Overdue</p>
          <p className="text-2xl font-bold text-red-600">{fmt(data?.overdue_amount || 0)}</p>
          <p className="text-xs text-gray-400 mt-1">{data?.overdue_count || 0} credits</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <p className="text-sm text-gray-500">Total Credits</p>
          <p className="text-2xl font-bold">{data?.total_credits || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Active Debtors</p>
          <p className="text-2xl font-bold">{data?.active_debtors || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Collection Rate</p>
          <p className="text-2xl font-bold">
            {data && data.total_amount_disbursed > 0
              ? Math.round((data.total_collected / data.total_amount_disbursed) * 100) + "%"
              : "0%"}
          </p>
        </div>
      </div>
    </div>
  );
}
