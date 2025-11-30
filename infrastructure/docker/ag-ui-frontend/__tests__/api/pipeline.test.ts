/**
 * Tests for /api/pipeline endpoint
 * 
 * Feature 1: Pipeline Creation Capability
 * Feature 3: Real-Time Pipeline Status
 * 
 * Tests:
 * - POST: Create new pipelines
 * - GET: List pipelines
 * - GET: Get specific pipeline by ID
 * - Pipeline execution and progress
 */

import { NextRequest } from 'next/server';

describe('Pipeline API (/api/pipeline)', () => {
  // Helper to create mock requests
  const createMockRequest = (
    method: string,
    body?: object,
    searchParams?: Record<string, string>
  ): NextRequest => {
    let url = 'http://localhost:3000/api/pipeline';
    if (searchParams) {
      const params = new URLSearchParams(searchParams);
      url += `?${params.toString()}`;
    }
    const init: RequestInit = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (body) {
      init.body = JSON.stringify(body);
    }
    return new Request(url, init) as unknown as NextRequest;
  };

  describe('POST /api/pipeline', () => {
    it('should create a new pipeline with valid topic', async () => {
      const { POST } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('POST', {
        topic: 'vector embeddings',
      });
      
      const response = await POST(request);
      const data = await response.json();
      
      expect(response.status).toBe(201);
      expect(data.success).toBe(true);
      expect(data.pipeline).toBeDefined();
      expect(data.pipeline.topic).toBe('vector embeddings');
      expect(data.pipeline.id).toMatch(/^pipeline-\d+-[a-z0-9]+$/);
      expect(data.pipeline.status).toMatch(/^(pending|running)$/);
      expect(data.pipeline.progress).toBe(0);
      expect(data.pipeline.currentPhase).toBe('research');
    });

    it('should return 400 when topic is missing', async () => {
      const { POST } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('POST', {});
      
      const response = await POST(request);
      const data = await response.json();
      
      expect(response.status).toBe(400);
      expect(data.error).toBe('Topic is required');
    });

    it('should return 400 when topic is empty', async () => {
      const { POST } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('POST', { topic: '   ' });
      
      const response = await POST(request);
      const data = await response.json();
      
      expect(response.status).toBe(400);
      expect(data.error).toBe('Topic is required');
    });

    it('should trim whitespace from topic', async () => {
      const { POST } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('POST', {
        topic: '  AI agents  ',
      });
      
      const response = await POST(request);
      const data = await response.json();
      
      expect(response.status).toBe(201);
      expect(data.pipeline.topic).toBe('AI agents');
    });

    it('should generate unique pipeline IDs', async () => {
      const { POST } = await import('@/app/api/pipeline/route');
      
      const request1 = createMockRequest('POST', { topic: 'topic 1' });
      const request2 = createMockRequest('POST', { topic: 'topic 2' });
      
      const response1 = await POST(request1);
      const response2 = await POST(request2);
      
      const data1 = await response1.json();
      const data2 = await response2.json();
      
      expect(data1.pipeline.id).not.toBe(data2.pipeline.id);
    });
  });

  describe('GET /api/pipeline', () => {
    it('should return list of pipelines', async () => {
      const { GET } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('GET');
      
      const response = await GET(request);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.pipelines).toBeDefined();
      expect(Array.isArray(data.pipelines)).toBe(true);
      expect(data.total).toBeDefined();
      expect(typeof data.activePipelinesCount).toBe('number');
    });

    it('should include completed pipeline in results', async () => {
      const { GET } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('GET');
      
      const response = await GET(request);
      const data = await response.json();
      
      const completedPipeline = data.pipelines.find(
        (p: { id: string }) => p.id === 'pipeline-demo-001'
      );
      expect(completedPipeline).toBeDefined();
      expect(completedPipeline.topic).toBe('Large Language Model Reasoning');
      expect(completedPipeline.status).toBe('completed');
    });

    it('should support limit parameter', async () => {
      const { GET } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('GET', undefined, { limit: '1' });
      
      const response = await GET(request);
      const data = await response.json();
      
      expect(data.pipelines.length).toBeLessThanOrEqual(1);
    });

    it('should support status filter', async () => {
      const { GET } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('GET', undefined, { status: 'completed' });
      
      const response = await GET(request);
      const data = await response.json();
      
      for (const pipeline of data.pipelines) {
        expect(pipeline.status).toBe('completed');
      }
    });

    it('should return specific pipeline by ID', async () => {
      const { GET } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('GET', undefined, { id: 'pipeline-demo-001' });
      
      const response = await GET(request);
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data.id).toBe('pipeline-demo-001');
      expect(data.topic).toBe('Large Language Model Reasoning');
    });

    it('should return 404 for non-existent pipeline ID', async () => {
      const { GET } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('GET', undefined, { id: 'non-existent-id' });
      
      const response = await GET(request);
      const data = await response.json();
      
      expect(response.status).toBe(404);
      expect(data.error).toBe('Pipeline not found');
    });
  });

  describe('Pipeline Data Structure', () => {
    it('should have all required fields in pipeline response', async () => {
      const { GET } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('GET', undefined, { id: 'pipeline-demo-001' });
      
      const response = await GET(request);
      const pipeline = await response.json();
      
      // Required fields
      expect(pipeline).toHaveProperty('id');
      expect(pipeline).toHaveProperty('topic');
      expect(pipeline).toHaveProperty('status');
      expect(pipeline).toHaveProperty('createdAt');
      expect(pipeline).toHaveProperty('updatedAt');
      expect(pipeline).toHaveProperty('progress');
      expect(pipeline).toHaveProperty('currentPhase');
    });

    it('should have results for completed pipeline', async () => {
      const { GET } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('GET', undefined, { id: 'pipeline-demo-001' });
      
      const response = await GET(request);
      const pipeline = await response.json();
      
      expect(pipeline.results).toBeDefined();
      expect(pipeline.results.research).toBeDefined();
      expect(pipeline.results.trends).toBeDefined();
      expect(pipeline.results.blog).toBeDefined();
    });

    it('should have valid status values', async () => {
      const { GET } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('GET');
      
      const response = await GET(request);
      const data = await response.json();
      
      const validStatuses = ['pending', 'running', 'completed', 'failed'];
      for (const pipeline of data.pipelines) {
        expect(validStatuses).toContain(pipeline.status);
      }
    });

    it('should have valid phase values', async () => {
      const { GET } = await import('@/app/api/pipeline/route');
      
      const request = createMockRequest('GET');
      
      const response = await GET(request);
      const data = await response.json();
      
      const validPhases = ['research', 'trends', 'writing', 'publishing', 'complete'];
      for (const pipeline of data.pipelines) {
        expect(validPhases).toContain(pipeline.currentPhase);
      }
    });
  });
});
