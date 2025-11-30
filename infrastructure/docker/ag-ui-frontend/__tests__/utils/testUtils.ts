/**
 * Test Utilities
 * 
 * Shared utilities for testing the AG-UI Frontend API routes.
 */

import { NextRequest } from 'next/server';

/**
 * Creates a mock NextRequest for testing API routes.
 * 
 * @param url - The URL to request
 * @param options - Request options (method, body, headers)
 * @returns A mock NextRequest object
 */
export function createMockRequest(
  url: string,
  options?: {
    method?: string;
    body?: object;
    headers?: Record<string, string>;
  }
): NextRequest {
  const init: RequestInit = {
    method: options?.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  };
  
  if (options?.body) {
    init.body = JSON.stringify(options.body);
  }
  
  return new Request(url, init) as unknown as NextRequest;
}

/**
 * Creates a mock request for the agent API.
 */
export function createAgentRequest(
  method: string,
  body?: object
): NextRequest {
  return createMockRequest('http://localhost:3000/api/agent', { method, body });
}

/**
 * Creates a mock request for the pipeline API.
 */
export function createPipelineRequest(
  method: string,
  body?: object,
  searchParams?: Record<string, string>
): NextRequest {
  let url = 'http://localhost:3000/api/pipeline';
  if (searchParams) {
    const params = new URLSearchParams(searchParams);
    url += `?${params.toString()}`;
  }
  return createMockRequest(url, { method, body });
}

/**
 * Waits for a specified number of milliseconds.
 * Useful for testing async operations.
 */
export function wait(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Extracts JSON from a Response object.
 */
export async function getResponseJson<T>(response: Response): Promise<T> {
  return response.json() as Promise<T>;
}

/**
 * Asserts that a response has a specific status code.
 */
export function expectStatus(response: Response, status: number): void {
  expect(response.status).toBe(status);
}

/**
 * Valid agent names for testing.
 */
export const VALID_AGENTS = ['research-agent', 'seo-agent', 'writer-agent'];

/**
 * Valid pipeline statuses.
 */
export const VALID_PIPELINE_STATUSES = ['pending', 'running', 'completed', 'failed'];

/**
 * Valid pipeline phases.
 */
export const VALID_PIPELINE_PHASES = ['research', 'trends', 'writing', 'publishing', 'complete'];
