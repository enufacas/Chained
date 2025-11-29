import { PipelineData } from "@/app/page";

interface PipelineResultProps {
  data: PipelineData;
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function PipelineResult({ data }: PipelineResultProps) {
  return (
    <div className="bg-slate-800 rounded-xl p-6 mb-8 border border-green-500/20">
      <h3 className="text-green-400 font-semibold mb-4 flex items-center gap-2">
        <span>📊</span> Pipeline Result
      </h3>
      <div className="grid md:grid-cols-4 gap-4">
        <div className="bg-black/30 p-4 rounded-lg">
          <p className="text-slate-500 text-xs uppercase mb-1">Context ID</p>
          <p className="text-white font-mono text-sm truncate" title={data.contextId}>
            {data.contextId}
          </p>
        </div>
        <div className="bg-black/30 p-4 rounded-lg">
          <p className="text-slate-500 text-xs uppercase mb-1">Status</p>
          <p className={`font-semibold ${data.success ? "text-green-400" : "text-red-400"}`}>
            {data.success ? "✅ Success" : "❌ Failed"}
          </p>
        </div>
        <div className="bg-black/30 p-4 rounded-lg">
          <p className="text-slate-500 text-xs uppercase mb-1">Tasks Completed</p>
          <p className="text-white font-semibold">{data.tasksCompleted}</p>
        </div>
        <div className="bg-black/30 p-4 rounded-lg">
          <p className="text-slate-500 text-xs uppercase mb-1">Completed At</p>
          <p className="text-white">{formatDate(data.completedAt)}</p>
        </div>
      </div>
    </div>
  );
}
