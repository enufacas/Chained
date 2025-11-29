/**
 * Agent styling utilities for consistent badge appearance.
 * Each agent type has its own color scheme and icon.
 */

export type AgentStyle = {
  bgColor: string;
  textColor: string;
  borderColor: string;
  icon: string;
  framework?: string;
};

export function getAgentStyle(agentName: string): AgentStyle {
  if (!agentName) {
    return {
      bgColor: "bg-gray-500/20",
      textColor: "text-gray-300",
      borderColor: "border-gray-500/30",
      icon: "🤖",
      framework: "",
    };
  }

  const nameLower = agentName.toLowerCase();

  // Academic Research Agent (green/emerald)
  if (nameLower.includes("research") || nameLower.includes("academic")) {
    return {
      bgColor: "bg-emerald-500/20",
      textColor: "text-emerald-400",
      borderColor: "border-emerald-500/30",
      icon: "🔬",
      framework: "ADK",
    };
  }

  // Google Trends Agent (blue)
  if (nameLower.includes("trend") || nameLower.includes("google")) {
    return {
      bgColor: "bg-blue-500/20",
      textColor: "text-blue-400",
      borderColor: "border-blue-500/30",
      icon: "📈",
      framework: "ADK",
    };
  }

  // Blog Writer Agent (purple/violet)
  if (nameLower.includes("blog") || nameLower.includes("writer")) {
    return {
      bgColor: "bg-violet-500/20",
      textColor: "text-violet-400",
      borderColor: "border-violet-500/30",
      icon: "✍️",
      framework: "ADK",
    };
  }

  // Orchestrator (gray/dark)
  if (nameLower.includes("orchestrator")) {
    return {
      bgColor: "bg-slate-700",
      textColor: "text-slate-200",
      borderColor: "border-slate-600",
      icon: "🎯",
      framework: "ADK",
    };
  }

  // Default style
  return {
    bgColor: "bg-gray-500/20",
    textColor: "text-gray-300",
    borderColor: "border-gray-500/30",
    icon: "🤖",
    framework: "A2A",
  };
}

export function truncateTask(text: string, maxLength: number = 100): string {
  if (!text) return "";
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + "...";
}

export function getAgentDisplayName(agentName: string): string {
  if (!agentName) return "Unknown Agent";
  
  const nameLower = agentName.toLowerCase();
  
  if (nameLower.includes("research") || nameLower.includes("academic")) {
    return "Academic Research";
  }
  if (nameLower.includes("trend") || nameLower.includes("google")) {
    return "Google Trends";
  }
  if (nameLower.includes("blog") || nameLower.includes("writer")) {
    return "Blog Writer";
  }
  
  return agentName;
}
