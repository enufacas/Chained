/**
 * Jest Setup File
 * 
 * This file runs after Jest is initialized but before tests are run.
 * It sets up global mocks and test utilities.
 */

// Extend Jest matchers
import '@testing-library/jest-dom';

// Mock Next.js request/response for API route testing
class MockNextRequest {
  url: string;
  method: string;
  headers: Map<string, string>;
  private body: string;

  constructor(url: string, init?: { method?: string; body?: string; headers?: Record<string, string> }) {
    this.url = url;
    this.method = init?.method || 'GET';
    this.body = init?.body || '';
    this.headers = new Map(Object.entries(init?.headers || {}));
  }

  async json() {
    return JSON.parse(this.body);
  }

  async text() {
    return this.body;
  }
}

// Make MockNextRequest available globally for tests
(global as Record<string, unknown>).MockNextRequest = MockNextRequest;

// Mock fetch for API tests
(global as Record<string, unknown>).fetch = jest.fn();

// Note: window, navigator, and localStorage are now provided by jsdom test environment
// No need to mock them manually

// Suppress console output during tests (optional)
// Uncomment to hide console logs during test runs
// global.console = {
//   ...console,
//   log: jest.fn(),
//   debug: jest.fn(),
//   info: jest.fn(),
//   warn: jest.fn(),
// };
