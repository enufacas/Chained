/**
 * Chained MCP Server - Model Context Protocol Implementation
 * 
 * This server exposes Chained agents as MCP-compatible tools,
 * enabling integration with Claude, Cursor, OpenAI, and other MCP clients.
 * 
 * @tools-analyst - JavaScript-AI-Agents Innovation
 */

import { EventEmitter } from 'events';
import * as fs from 'fs/promises';
import * as path from 'path';

// ============================================================================
// MCP Protocol Types (Simplified for POC)
// ============================================================================

interface MCPTool {
  name: string;
  description: string;
  inputSchema: {
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
}

interface MCPServer {
  name: string;
  version: string;
  tools: MCPTool[];
}

interface ChainedAgent {
  name: string;
  description: string;
  personality: {
    name: string;
    traits: string[];
    communicationStyle: string;
  };
  specialization: string[];
  coreResponsibilities: string[];
}

// ============================================================================
// Chained MCP Server Implementation
// ============================================================================

export class ChainedMCPServer extends EventEmitter implements MCPServer {
  name = 'chained-agents';
  version = '1.0.0';
  
  private agents: Map<string, ChainedAgent> = new Map();
  private agentsLoaded = false;
  
  constructor() {
    super();
  }
  
  /**
   * Load Chained agents from .github/agents/ directory
   */
  async loadAgents(): Promise<void> {
    if (this.agentsLoaded) return;
    
    const agentsDir = path.join(process.cwd(), '.github', 'agents');
    
    try {
      const files = await fs.readdir(agentsDir);
      const mdFiles = files.filter(f => f.endsWith('.md') && f !== 'README.md');
      
      for (const file of mdFiles) {
        const agentPath = path.join(agentsDir, file);
        const content = await fs.readFile(agentPath, 'utf-8');
        const agent = this.parseAgentMarkdown(content, file);
        
        if (agent) {
          this.agents.set(agent.name, agent);
          this.emit('agent:loaded', agent);
        }
      }
      
      this.agentsLoaded = true;
      this.emit('server:ready', { agentCount: this.agents.size });
      
    } catch (error) {
      this.emit('server:error', error);
      throw new Error(`Failed to load agents: ${error.message}`);
    }
  }
  
  /**
   * Parse agent definition from Markdown file
   */
  private parseAgentMarkdown(content: string, filename: string): ChainedAgent | null {
    try {
      const name = filename.replace('.md', '');
      
      // Extract description (first paragraph after header)
      const descMatch = content.match(/^#.*?\n\n(.*?)\n\n/ms);
      const description = descMatch ? descMatch[1].trim() : 'Chained AI Agent';
      
      // Extract personality info
      const personalityMatch = content.match(/\*\*Personality:\*\* (.*?)$/m);
      const traitsMatch = content.match(/\*\*Traits:\*\* (.*?)$/m);
      const styleMatch = content.match(/\*\*Communication Style:\*\* (.*?)$/m);
      
      // Extract core responsibilities
      const responsibilitiesMatch = content.match(/## Core Responsibilities\n\n(.*?)(?=\n##|$)/s);
      const responsibilities: string[] = [];
      
      if (responsibilitiesMatch) {
        const matches = responsibilitiesMatch[1].matchAll(/\d+\.\s+\*\*(.*?)\*\*/g);
        for (const match of matches) {
          responsibilities.push(match[1]);
        }
      }
      
      return {
        name,
        description,
        personality: {
          name: name,
          traits: traitsMatch ? traitsMatch[1].split(',').map(t => t.trim()) : [],
          communicationStyle: styleMatch ? styleMatch[1].trim() : 'professional'
        },
        specialization: [name.replace('-', ' ')],
        coreResponsibilities: responsibilities
      };
      
    } catch (error) {
      console.error(`Failed to parse agent ${filename}:`, error);
      return null;
    }
  }
  
  /**
   * Get MCP tools definition (one tool per agent)
   */
  get tools(): MCPTool[] {
    return Array.from(this.agents.values()).map(agent => ({
      name: `invoke_${agent.name.replace(/-/g, '_')}`,
      description: `${agent.description}\n\nSpecialization: ${agent.specialization.join(', ')}\n\nCore capabilities:\n${agent.coreResponsibilities.map((r, i) => `${i + 1}. ${r}`).join('\n')}`,
      inputSchema: {
        type: 'object',
        properties: {
          task: {
            type: 'string',
            description: 'Task description for the agent to perform'
          },
          context: {
            type: 'object',
            description: 'Additional context about the task (optional)',
            properties: {
              files: {
                type: 'array',
                items: { type: 'string' },
                description: 'Relevant file paths'
              },
              references: {
                type: 'array',
                items: { type: 'string' },
                description: 'Related issues or PRs'
              },
              priority: {
                type: 'string',
                enum: ['low', 'medium', 'high', 'critical'],
                description: 'Task priority level'
              }
            }
          }
        },
        required: ['task']
      }
    }));
  }
  
  /**
   * Invoke a Chained agent via MCP
   */
  async invokeAgent(agentName: string, params: {
    task: string;
    context?: {
      files?: string[];
      references?: string[];
      priority?: 'low' | 'medium' | 'high' | 'critical';
    };
  }): Promise<{
    status: 'queued' | 'in_progress' | 'completed' | 'failed';
    issueNumber?: number;
    issueUrl?: string;
    message: string;
  }> {
    const agent = this.agents.get(agentName);
    
    if (!agent) {
      throw new Error(`Agent ${agentName} not found. Available agents: ${Array.from(this.agents.keys()).join(', ')}`);
    }
    
    this.emit('agent:invoke', { agentName, task: params.task });
    
    // In a real implementation, this would:
    // 1. Create a GitHub issue with agent assignment
    // 2. Wait for workflow to pick it up
    // 3. Monitor progress
    // 4. Return results
    
    // For now, return mock response
    return {
      status: 'queued',
      message: `Task queued for @${agentName}. Agent will begin processing shortly.`,
      issueNumber: Math.floor(Math.random() * 1000), // Mock
      issueUrl: `https://github.com/enufacas/Chained/issues/${Math.floor(Math.random() * 1000)}`
    };
  }
  
  /**
   * Get agent information
   */
  getAgent(name: string): ChainedAgent | undefined {
    return this.agents.get(name);
  }
  
  /**
   * List all available agents
   */
  listAgents(): ChainedAgent[] {
    return Array.from(this.agents.values());
  }
  
  /**
   * Get server info (MCP protocol)
   */
  getServerInfo(): MCPServer {
    return {
      name: this.name,
      version: this.version,
      tools: this.tools
    };
  }
}

// ============================================================================
// CLI Interface (for testing)
// ============================================================================

async function main() {
  console.log('🤖 Chained MCP Server - JavaScript-AI-Agents Innovation\n');
  console.log('Initializing Model Context Protocol server...\n');
  
  const server = new ChainedMCPServer();
  
  // Event listeners
  server.on('agent:loaded', (agent) => {
    console.log(`✅ Loaded agent: @${agent.name}`);
  });
  
  server.on('server:ready', ({ agentCount }) => {
    console.log(`\n🚀 Server ready with ${agentCount} agents\n`);
    console.log('Available MCP Tools:');
    server.tools.forEach((tool, index) => {
      console.log(`  ${index + 1}. ${tool.name}`);
    });
  });
  
  server.on('server:error', (error) => {
    console.error('❌ Server error:', error.message);
  });
  
  // Load agents
  try {
    await server.loadAgents();
    
    // Example: List agents
    console.log('\n📋 Agent Registry:');
    server.listAgents().forEach(agent => {
      console.log(`  • @${agent.name}: ${agent.description}`);
    });
    
    // Example: Get specific agent
    const toolsAnalyst = server.getAgent('tools-analyst');
    if (toolsAnalyst) {
      console.log('\n🔨 Tools Analyst Agent:');
      console.log(`  Personality: ${toolsAnalyst.personality.traits.join(', ')}`);
      console.log(`  Style: ${toolsAnalyst.personality.communicationStyle}`);
      console.log(`  Responsibilities:`);
      toolsAnalyst.coreResponsibilities.forEach((r, i) => {
        console.log(`    ${i + 1}. ${r}`);
      });
    }
    
    // Example: Invoke agent (mock)
    console.log('\n🎯 Example MCP Tool Invocation:');
    const result = await server.invokeAgent('tools-analyst', {
      task: 'Research JavaScript-AI-Agents integration patterns',
      context: {
        priority: 'high',
        references: ['#123']
      }
    });
    console.log(`  Status: ${result.status}`);
    console.log(`  Message: ${result.message}`);
    console.log(`  Issue: ${result.issueUrl}`);
    
  } catch (error) {
    console.error('\n❌ Fatal error:', error.message);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

export default ChainedMCPServer;
