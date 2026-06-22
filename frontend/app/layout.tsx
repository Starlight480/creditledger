import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CreditLedger — Credit Sales Management",
  description: "Track credit sales, manage debtors, and collect payments for your Nigerian business.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50">{children}</body>
    </html>
  );
}
