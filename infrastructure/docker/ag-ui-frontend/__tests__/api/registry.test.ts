/**
 * Registry API Tests
 * 
 * Tests for /api/registry endpoint
 */

import { NextRequest } from 'next/server';

describe('Registry API (/api/registry)', () => {
  let GET: (request: NextRequest) => Promise<Response>;
  let POST: (request: NextRequest) => Promise<Response>;

  beforeAll(async () => {
    const module = await import('@/app/api/registry/route');
    GET = module.GET;
    POST = module.POST;
  });

  // Helper to create a mock NextRequest
  // Note: This uses type assertion as NextRequest has many internal properties
  // that are not relevant for testing. In production code, consider using a
  // proper mock library or testing utility for better type safety.
  const createMockRequest = (method: string, body?: object, searchParams?: URLSearchParams): NextRequest => {
    const url = searchParams 
      ? `http://localhost:3000/api/registry?${searchParams.toString()}`
      : 'http://localhost:3000/api/registry';
    
    return new Request(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    }) as unknown as NextRequest;
  };

  describe('GET /api/registry', () => {
    it('should return list of all agents', async () => {
      const request = createMockRequest('GET');
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.agents).toBeDefined();
      expect(Array.isArray(data.agents)).toBe(true);
      expect(data.agents.length).toBeGreaterThan(0);
    });

    it('should return agents with required fields', async () => {
      const request = createMockRequest('GET');
      const response = await GET(request);
      const data = await response.json();

      const agent = data.agents[0];
      expect(agent).toHaveProperty('id');
      expect(agent).toHaveProperty('displayName');
      expect(agent).toHaveProperty('description');
      expect(agent).toHaveProperty('icon');
      expect(agent).toHaveProperty('category');
      expect(agent).toHaveProperty('skills');
    });

    it('should include well-known agent IDs', async () => {
      const request = createMockRequest('GET');
      const response = await GET(request);
      const data = await response.json();

      const agentIds = data.agents.map((agent: { id: string }) => agent.id);
      
      // Check for expected agents
      expect(agentIds).toContain('academic-research');
      expect(agentIds).toContain('google-trends');
      expect(agentIds).toContain('blog-writer');
    });

    it('should get specific agent by ID', async () => {
      const params = new URLSearchParams({ id: 'academic-research' });
      const request = createMockRequest('GET', undefined, params);
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.agent).toBeDefined();
      expect(data.agent.id).toBe('academic-research');
      expect(data.agent.displayName).toBe('Academic Research');
    });

    it('should return 404 for unknown agent ID', async () => {
      const params = new URLSearchParams({ id: 'non-existent-agent' });
      const request = createMockRequest('GET', undefined, params);
      const response = await GET(request);

      expect(response.status).toBe(404);
    });

    it('should include agent URLs in response', async () => {
      const request = createMockRequest('GET');
      const response = await GET(request);
      const data = await response.json();

      const agent = data.agents[0];
      expect(agent).toHaveProperty('url');
    });
  });

  describe('POST /api/registry', () => {
    beforeEach(() => {
      // Mock fetch for health checks
      global.fetch = jest.fn();
    });

    afterEach(() => {
      jest.restoreAllMocks();
    });

    it('should check agent health', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ status: 'healthy' }),
      });

      const request = createMockRequest('POST', {
        agentId: 'academic-research',
      });

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data).toHaveProperty('healthy');
      expect(data.agentId).toBe('academic-research');
    });

    it('should return 400 for missing agentId', async () => {
      const request = createMockRequest('POST', {});
      const response = await POST(request);

      expect(response.status).toBe(400);
    });

    it('should return 404 for unknown agent', async () => {
      const request = createMockRequest('POST', {
        agentId: 'unknown-agent',
      });

      const response = await POST(request);

      expect(response.status).toBe(404);
    });

    it('should handle agent health check failure', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      const request = createMockRequest('POST', {
        agentId: 'academic-research',
      });

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.healthy).toBe(false);
      expect(data.error).toBeDefined();
    });

    it('should handle non-200 status from health endpoint', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 503,
        statusText: 'Service Unavailable',
      });

      const request = createMockRequest('POST', {
        agentId: 'academic-research',
      });

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.healthy).toBe(false);
    });
  });

  describe('Agent categories', () => {
    it('should have agents in different categories', async () => {
      const request = createMockRequest('GET');
      const response = await GET(request);
      const data = await response.json();

      const categories = [...new Set(data.agents.map((agent: { category: string }) => agent.category))];
      
      expect(categories.length).toBeGreaterThan(1);
      expect(categories).toContain('research');
    });
  });

  describe('Agent skills', () => {
    it('should include skills array for each agent', async () => {
      const request = createMockRequest('GET');
      const response = await GET(request);
      const data = await response.json();

      data.agents.forEach((agent: { skills: string[] }) => {
        expect(Array.isArray(agent.skills)).toBe(true);
        expect(agent.skills.length).toBeGreaterThan(0);
      });
    });
  });
});
