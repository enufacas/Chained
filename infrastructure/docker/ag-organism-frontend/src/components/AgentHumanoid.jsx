import React, { useMemo } from 'react';
import ProceduralRobotModel from './ProceduralRobotModel';

function AgentHumanoid({ agent, position, isSelected, state }) {
  // Get color based on agent
  const color = useMemo(() => {
    // Factory theme colors - blues and silvers
    const colors = {
      'academic-research': 0x60a5fa,   // Blue
      'google-trends': 0x818cf8,       // Indigo
      'blog-writer': 0x34d399,         // Emerald
      'code-reviewer': 0xa78bfa,       // Violet
      'data-analyst': 0x38bdf8,        // Sky blue
      'image-generator': 0xf472b6,     // Pink
    };
    return colors[agent.id] || 0x60a5fa; // Default blue
  }, [agent.id]);

  // Map agent types to robot variants
  const variant = useMemo(() => {
    const variants = {
      'academic-research': 'scientist',
      'google-trends': 'analyst',
      'blog-writer': 'writer',
      'code-reviewer': 'engineer',
      'data-analyst': 'analyst',
      'image-generator': 'artist'
    };
    return variants[agent.id] || 'worker';
  }, [agent.id]);

  return (
    <ProceduralRobotModel
      variant={variant}
      state={state}
      color={color}
      isSelected={isSelected}
    />
  );
}

export default AgentHumanoid;
