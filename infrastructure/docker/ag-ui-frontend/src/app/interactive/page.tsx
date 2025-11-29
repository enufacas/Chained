/**
 * Interactive Page - Redirects to main unified page
 * 
 * This page previously had a separate implementation for interactive A2A pipeline chat.
 * It has been consolidated into the main page for simplicity.
 */

"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function InteractivePage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to main page after a short delay
    const timer = setTimeout(() => {
      router.push("/");
    }, 3000);
    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white flex items-center justify-center">
      <div className="text-center max-w-md p-8">
        <div className="text-6xl mb-4">🔄</div>
        <h1 className="text-2xl font-bold text-accent-400 mb-4">Page Consolidated</h1>
        <p className="text-slate-400 mb-6">
          The interactive page has been merged into the main AG-UI page for a simpler, unified experience.
        </p>
        <p className="text-slate-500 text-sm mb-6">
          Redirecting in 3 seconds...
        </p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 px-6 py-3 bg-accent-500/20 border border-accent-500/50 rounded-lg text-accent-300 hover:bg-accent-500/30 transition font-medium"
        >
          🏠 Go to Main Page Now
        </Link>
      </div>
    </div>
  );
}
