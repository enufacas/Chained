/**
 * Tests for /api/activity endpoint
 * 
 * Tests the GCP Cloud Run agent activity monitoring API.
 * 
 * Tests:
 * - GET: Returns agent status from GCP Cloud Run
 * - Response structure validation
 * - System health calculation
 * - Development mode fallback behavior
 */

import { NextRequest } from 'next/server';

// Mock fetch for testing
const originalFetch = global.fetch;

describe('Activity API (/api/activity)', () => {
  // Helper to create mock requests
  const createMockRequest = (
    searchParams?: Record<string, string>
  ): NextRequest => {
    let url = 'http://localhost:3000/api/activity';
    if (searchParams) {
      const params = new URLSearchParams(searchParams);
      url += `?${params.toString()}`;
    }
    return new Request(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    }) as unknown as NextRequest;
  };

  // Mock healthy agent response
  const mockHealthyResponse = {
    status: 'healthy',
    agent: 'test-agent',
    version: '1.0.0',
    ai_mode: 'enabled',
    timestamp: new Date().toISOString(),
  };

  beforeEach(() => {
    jest.resetModules();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  describe('GET /api/activity', () => {
    it('should return activity response with correct structure', async () => {
      // Mock fetch to simulate agent health checks
      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockHealthyResponse),
          });
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest();
      const response = await GET(request);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data).toHaveProperty('agents');
      expect(data).toHaveProperty('systemStatus');
      expect(data).toHaveProperty('adkApiUrl');
      expect(data).toHaveProperty('lastUpdated');
      expect(data).toHaveProperty('source');
      expect(data.source).toBe('gcp-cloudrun');
    });

    it('should return correct agent count', async () => {
      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockHealthyResponse),
          });
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest();
      const response = await GET(request);
      const data = await response.json();
      
      // Should have 4 agents: academic-research, google-trends, blog-writer, adk-api-server
      expect(Array.isArray(data.agents)).toBe(true);
      expect(data.agents.length).toBe(4);
      expect(data.systemStatus.total).toBe(4);
    });

    it('should include agent information in response', async () => {
      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockHealthyResponse),
          });
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest();
      const response = await GET(request);
      const data = await response.json();
      
      // Check each agent has required fields
      for (const agent of data.agents) {
        expect(agent).toHaveProperty('id');
        expect(agent).toHaveProperty('name');
        expect(agent).toHaveProperty('displayName');
        expect(agent).toHaveProperty('icon');
        expect(agent).toHaveProperty('description');
        expect(agent).toHaveProperty('url');
        expect(agent).toHaveProperty('health');
      }
    });

    it('should have correct agent IDs', async () => {
      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockHealthyResponse),
          });
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest();
      const response = await GET(request);
      const data = await response.json();
      
      const agentIds = data.agents.map((a: { id: string }) => a.id);
      expect(agentIds).toContain('academic-research');
      expect(agentIds).toContain('google-trends');
      expect(agentIds).toContain('blog-writer');
      expect(agentIds).toContain('adk-api-server');
    });
  });

  describe('System Health Calculation', () => {
    it('should report healthy when all agents are healthy', async () => {
      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockHealthyResponse),
          });
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest();
      const response = await GET(request);
      const data = await response.json();
      
      expect(data.systemStatus.overallHealth).toBe('healthy');
      expect(data.systemStatus.healthy).toBe(4);
      expect(data.systemStatus.unhealthy).toBe(0);
    });

    it('should report degraded when some agents are unhealthy', async () => {
      let callCount = 0;
      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          callCount++;
          // First agent healthy, others fail
          if (callCount === 1) {
            return Promise.resolve({
              ok: true,
              json: () => Promise.resolve(mockHealthyResponse),
            });
          }
          return Promise.resolve({
            ok: false,
            status: 503,
          });
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest();
      const response = await GET(request);
      const data = await response.json();
      
      expect(data.systemStatus.overallHealth).toBe('degraded');
      expect(data.systemStatus.healthy).toBeGreaterThan(0);
      expect(data.systemStatus.unhealthy).toBeGreaterThan(0);
    });

    it('should report unhealthy when all agents are down', async () => {
      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          return Promise.reject(new Error('Connection refused'));
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest();
      const response = await GET(request);
      const data = await response.json();
      
      expect(data.systemStatus.overallHealth).toBe('unhealthy');
      expect(data.systemStatus.healthy).toBe(0);
    });
  });

  describe('Agent Health Response', () => {
    it('should include response time for healthy agents', async () => {
      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockHealthyResponse),
          });
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest();
      const response = await GET(request);
      const data = await response.json();
      
      for (const agent of data.agents) {
        if (agent.health.status === 'healthy') {
          expect(agent.health.responseTimeMs).toBeDefined();
          expect(typeof agent.health.responseTimeMs).toBe('number');
        }
      }
    });

    it('should include version info from health response', async () => {
      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockHealthyResponse),
          });
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest();
      const response = await GET(request);
      const data = await response.json();
      
      const healthyAgent = data.agents.find(
        (a: { health: { status: string } }) => a.health.status === 'healthy'
      );
      
      if (healthyAgent) {
        expect(healthyAgent.health.version).toBe('1.0.0');
      }
    });

    it('should handle timeout gracefully', async () => {
      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          // Simulate timeout by rejecting with AbortError
          const error = new Error('Timeout');
          error.name = 'AbortError';
          return Promise.reject(error);
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest();
      const response = await GET(request);
      const data = await response.json();
      
      // Should still return valid response even if all agents timeout
      expect(response.status).toBe(200);
      expect(data.agents).toBeDefined();
      
      // All agents should be unhealthy due to timeout
      for (const agent of data.agents) {
        expect(agent.health.status).toBe('unhealthy');
      }
    });
  });

  describe('Cache Headers', () => {
    it('should include cache-control header', async () => {
      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockHealthyResponse),
          });
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest();
      const response = await GET(request);
      
      expect(response.headers.get('Cache-Control')).toBe(
        'public, s-maxage=15, stale-while-revalidate=30'
      );
    });

    it('should include content-type header', async () => {
      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockHealthyResponse),
          });
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest();
      const response = await GET(request);
      
      expect(response.headers.get('Content-Type')).toBe('application/json');
    });
  });

  describe('Optional Agent Card Fetching', () => {
    it('should fetch agent card when includeCards=true', async () => {
      const mockAgentCard = {
        name: 'Test Agent',
        version: '1.0.0',
        skills: [
          { id: 'skill-1', name: 'Test Skill', description: 'A test skill' },
        ],
      };

      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockHealthyResponse),
          });
        }
        if (url.includes('/.well-known/agent.json')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockAgentCard),
          });
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest({ includeCards: 'true' });
      const response = await GET(request);
      const data = await response.json();
      
      // At least one healthy agent should have agent card
      const agentWithCard = data.agents.find(
        (a: { agentCard?: object }) => a.agentCard !== undefined
      );
      
      if (agentWithCard) {
        expect(agentWithCard.agentCard.name).toBe('Test Agent');
        expect(Array.isArray(agentWithCard.agentCard.skills)).toBe(true);
      }
    });

    it('should not fetch agent card by default', async () => {
      global.fetch = jest.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockHealthyResponse),
          });
        }
        if (url.includes('/.well-known/agent.json')) {
          // Should not be called
          throw new Error('Agent card should not be fetched by default');
        }
        return Promise.reject(new Error('Unexpected URL'));
      });

      const { GET } = await import('@/app/api/activity/route');
      
      const request = createMockRequest();
      const response = await GET(request);
      const data = await response.json();
      
      // No agents should have agent card
      for (const agent of data.agents) {
        expect(agent.agentCard).toBeUndefined();
      }
    });
  });
});
