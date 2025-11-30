/**
 * Tests for /api/agent endpoint
 * 
 * Feature 2: Direct Agent Interaction
 * 
 * Tests:
 * - GET: List available agents
 * - POST: Send messages to specific agents with @agent-name syntax
 * - POST: Handle missing agent mentions
 * - POST: Handle unknown agents
 */

import { NextRequest } from 'next/server';

// Import the route handlers
// Note: We need to mock NextRequest for these tests
describe('Agent API (/api/agent)', () => {
  // Helper to create mock requests
  const createMockRequest = (method: string, body?: object): NextRequest => {
    const url = 'http://localhost:3000/api/agent';
    const init: RequestInit = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (body) {
      init.body = JSON.stringify(body);
    }
    return new Request(url, init) as unknown as NextRequest;
  };

  describe('GET /api/agent', () => {
    it('should return list of available agents', async () => {
      // Import dynamically to avoid module resolution issues
      const { GET } = await import('@/app/api/agent/route');
      
      const response = await GET();
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.agents).toBeDefined();
      expect(Array.isArray(data.agents)).toBe(true);
      expect(data.agents.length).toBeGreaterThan(0);
    });

    it('should include all required agent fields', async () => {
      const { GET } = await import('@/app/api/agent/route');
      
      const response = await GET();
      const data = await response.json();
      
      const agent = data.agents[0];
      expect(agent).toHaveProperty('name');
      expect(agent).toHaveProperty('displayName');
      expect(agent).toHaveProperty('description');
      expect(agent).toHaveProperty('icon');
      expect(agent).toHaveProperty('capabilities');
      expect(agent).toHaveProperty('examplePrompts');
    });

    it('should include usage examples', async () => {
      const { GET } = await import('@/app/api/agent/route');
      
      const response = await GET();
      const data = await response.json();
      
      expect(data.usage).toBeDefined();
      expect(data.usage.syntax).toBe('@agent-name your query here');
      expect(data.usage.examples).toBeDefined();
      expect(Array.isArray(data.usage.examples)).toBe(true);
    });

    it('should have research-agent, seo-agent, and writer-agent', async () => {
      const { GET } = await import('@/app/api/agent/route');
      
      const response = await GET();
      const data = await response.json();
      
      const agentNames = data.agents.map((a: { name: string }) => a.name);
      expect(agentNames).toContain('research-agent');
      expect(agentNames).toContain('seo-agent');
      expect(agentNames).toContain('writer-agent');
    });
  });

  describe('POST /api/agent', () => {
    it('should parse @research-agent mention and return response', async () => {
      const { POST } = await import('@/app/api/agent/route');
      
      const request = createMockRequest('POST', {
        message: '@research-agent What are the trends in AI?',
      });
      
      const response = await POST(request);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.type).toBe('agent_response');
      expect(data.agent.name).toBe('research-agent');
      expect(data.query).toBe('What are the trends in AI?');
      expect(data.response).toBeDefined();
    });

    it('should parse @seo-agent mention and return keyword analysis', async () => {
      const { POST } = await import('@/app/api/agent/route');
      
      const request = createMockRequest('POST', {
        message: '@seo-agent Suggest keywords for machine learning',
      });
      
      const response = await POST(request);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.type).toBe('agent_response');
      expect(data.agent.name).toBe('seo-agent');
      expect(data.response).toContain('Keyword');
    });

    it('should parse @writer-agent mention and return draft', async () => {
      const { POST } = await import('@/app/api/agent/route');
      
      const request = createMockRequest('POST', {
        message: '@writer-agent Draft an introduction on transformers',
      });
      
      const response = await POST(request);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.type).toBe('agent_response');
      expect(data.agent.name).toBe('writer-agent');
      expect(data.response).toContain('Draft');
    });

    it('should return help when no agent is mentioned', async () => {
      const { POST } = await import('@/app/api/agent/route');
      
      const request = createMockRequest('POST', {
        message: 'What are the trends in AI?',
      });
      
      const response = await POST(request);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.type).toBe('help');
      expect(data.availableAgents).toBeDefined();
      expect(data.examples).toBeDefined();
    });

    it('should return 404 for unknown agent', async () => {
      const { POST } = await import('@/app/api/agent/route');
      
      const request = createMockRequest('POST', {
        message: '@unknown-agent Do something',
      });
      
      const response = await POST(request);
      const data = await response.json();
      
      expect(response.status).toBe(404);
      expect(data.type).toBe('error');
      expect(data.availableAgents).toBeDefined();
    });

    it('should return 400 when message is missing', async () => {
      const { POST } = await import('@/app/api/agent/route');
      
      const request = createMockRequest('POST', {});
      
      const response = await POST(request);
      
      expect(response.status).toBe(400);
    });

    it('should support explicit agentName parameter', async () => {
      const { POST } = await import('@/app/api/agent/route');
      
      const request = createMockRequest('POST', {
        message: 'What are the trends?',
        agentName: 'research-agent',
      });
      
      const response = await POST(request);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.type).toBe('agent_response');
      expect(data.agent.name).toBe('research-agent');
    });
  });
});
