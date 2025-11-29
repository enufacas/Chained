"use client";

import { useState } from "react";
import { PipelineData } from "@/types";

interface DataPreviewProps {
  data: PipelineData;
}

type TabKey = "research" | "trends" | "blog" | "full";

export function DataPreview({ data }: DataPreviewProps) {
  const [activeTab, setActiveTab] = useState<TabKey>("research");

  const tabs: { key: TabKey; label: string }[] = [
    { key: "research", label: "Research" },
    { key: "trends", label: "Trends" },
    { key: "blog", label: "Blog" },
    { key: "full", label: "Full Result" },
  ];

  const getTabData = () => {
    switch (activeTab) {
      case "research":
        return data.research;
      case "trends":
        return data.trends;
      case "blog":
        return data.blog;
      default:
        return data;
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl p-6 mb-8 border border-slate-700">
      <h3 className="text-primary-400 font-semibold mb-4 flex items-center gap-2">
        <span>📦</span> Data Preview
      </h3>
      
      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-4">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-lg border transition-all ${
              activeTab === tab.key
                ? "bg-primary-500 border-primary-500 text-white"
                : "bg-primary-500/10 border-primary-500/30 text-slate-300 hover:bg-primary-500/20"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="bg-black/50 rounded-lg p-4 max-h-96 overflow-auto">
        <pre className="text-slate-300 text-sm whitespace-pre-wrap font-mono">
          {JSON.stringify(getTabData(), null, 2)}
        </pre>
      </div>
    </div>
  );
}
