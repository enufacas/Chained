import { PipelineRun } from "@/app/page";

interface RunSelectorProps {
  runs: PipelineRun[];
  selectedRun: number;
  onSelectRun: (runId: number) => void;
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function RunSelector({ runs, selectedRun, onSelectRun }: RunSelectorProps) {
  return (
    <div className="bg-slate-800 rounded-xl p-6 mb-8 border border-slate-700">
      <h3 className="text-primary-400 font-semibold mb-4">📋 Select Pipeline Run</h3>
      <div className="flex flex-wrap gap-3">
        {runs.map((run) => (
          <button
            key={run.id}
            onClick={() => onSelectRun(run.id)}
            className={`px-4 py-2 rounded-lg border transition-all ${
              selectedRun === run.id
                ? "bg-primary-500 border-primary-500 text-white"
                : "bg-primary-500/10 border-primary-500/30 text-slate-300 hover:bg-primary-500/20"
            }`}
          >
            <span
              className={`inline-block w-2 h-2 rounded-full mr-2 ${
                run.conclusion === "success" ? "bg-green-400" : "bg-red-400"
              }`}
            />
            Run #{run.runNumber}
            <span className="text-xs ml-2 opacity-70">{formatDate(run.createdAt)}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
