import { Agent } from "@/app/page";

interface AgentCardProps {
  agent: Agent;
}

const statusColors = {
  pending: "bg-slate-500",
  working: "bg-yellow-500",
  completed: "bg-green-500",
  failed: "bg-red-500",
};

export function AgentCard({ agent }: AgentCardProps) {
  return (
    <div className="bg-slate-800 rounded-xl border border-primary-500/20 overflow-hidden hover:border-primary-500/50 transition-all hover:-translate-y-1 hover:shadow-lg hover:shadow-primary-500/10 h-full">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-500/10 to-accent-500/10 p-4 border-b border-primary-500/20">
        <div className="text-4xl mb-2">{agent.icon}</div>
        <h3 className="text-primary-400 font-bold text-lg">{agent.name}</h3>
        <p className="text-slate-500 text-xs font-mono">{agent.id}</p>
      </div>

      {/* Body */}
      <div className="p-4 space-y-4">
        <p className="text-slate-400 text-sm">{agent.description}</p>

        {/* Skills */}
        <div>
          <p className="text-slate-500 text-xs uppercase tracking-wider mb-2">
            Skills
          </p>
          <div className="flex flex-wrap gap-2">
            {agent.skills.map((skill) => (
              <span
                key={skill}
                className="bg-accent-500/20 text-accent-400 px-2 py-1 rounded-full text-xs border border-accent-500/30"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* Task Status */}
        <div className="bg-black/30 rounded-lg p-3">
          <div className="flex justify-between items-center mb-2">
            <span className="text-slate-500 text-xs uppercase">Task Status</span>
            <span
              className={`${statusColors[agent.status]} px-2 py-0.5 rounded-full text-xs text-white capitalize`}
            >
              {agent.status}
            </span>
          </div>
          <code className="text-slate-400 text-xs bg-black/50 p-2 rounded block truncate">
            {agent.taskId || "-"}
          </code>
        </div>

        {/* Artifacts */}
        <div>
          <p className="text-slate-500 text-xs uppercase tracking-wider mb-2">
            Artifacts
          </p>
          <div className="space-y-2">
            {agent.artifacts.map((artifact) => (
              <div
                key={artifact.name}
                className="flex items-center gap-2 bg-primary-500/10 p-2 rounded"
              >
                <span className="text-primary-400">📄</span>
                <span className="text-slate-300 text-sm flex-1 truncate">
                  {artifact.name}
                </span>
                <span className="text-slate-500 text-xs">{artifact.type}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
