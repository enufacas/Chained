import React, { useMemo } from 'react';
import * as THREE from 'three';

function ConnectionLines({ agents, selectedAgents, agentStates, showConnections }) {
  const lines = useMemo(() => {
    if (!showConnections || selectedAgents.size < 2) return [];

    const selected = Array.from(selectedAgents);
    const lineData = [];

    for (let i = 0; i < selected.length - 1; i++) {
      const agent1 = agents.find(a => a.id === selected[i]);
      const agent2 = agents.find(a => a.id === selected[i + 1]);

      if (agent1 && agent2) {
        const index1 = agents.indexOf(agent1);
        const index2 = agents.indexOf(agent2);
        
        const radius = 20;
        const angle1 = (index1 / agents.length) * Math.PI * 2;
        const angle2 = (index2 / agents.length) * Math.PI * 2;

        const pos1 = [Math.cos(angle1) * radius, 0, Math.sin(angle1) * radius];
        const pos2 = [Math.cos(angle2) * radius, 0, Math.sin(angle2) * radius];

        lineData.push({ pos1, pos2, key: `${selected[i]}-${selected[i + 1]}` });
      }
    }

    return lineData;
  }, [agents, selectedAgents, showConnections]);

  if (!showConnections) return null;

  return (
    <group>
      {lines.map(({ pos1, pos2, key }) => {
        const points = [new THREE.Vector3(...pos1), new THREE.Vector3(...pos2)];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);

        return (
          <line key={key} geometry={geometry}>
            <lineBasicMaterial color={0xff00ff} transparent opacity={0.6} />
          </line>
        );
      })}
    </group>
  );
}

export default ConnectionLines;
