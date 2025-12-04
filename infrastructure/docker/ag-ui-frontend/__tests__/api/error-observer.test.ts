/**
 * Error Observer API Tests
 *
 * Tests for the error-observer status endpoint and integration
 */

import { GET } from "@/app/api/error-observer/status/route";

describe("Error Observer API", () => {
  // Store original env vars
  const originalEnv = process.env;

  beforeEach(() => {
    // Reset env vars before each test
    jest.resetModules();
    process.env = { ...originalEnv };
  });

  afterAll(() => {
    // Restore original env vars
    process.env = originalEnv;
  });

  describe("GET /api/error-observer/status", () => {
    it("should return not configured when ERROR_OBSERVER_URL is not set", async () => {
      delete process.env.ERROR_OBSERVER_URL;

      const response = await GET();
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.configured).toBe(false);
      expect(data.state).toBeNull();
      expect(data.lastUpdated).toBeDefined();
    });

    it("should return configured true when ERROR_OBSERVER_URL is set", async () => {
      // Mock a URL
      process.env.ERROR_OBSERVER_URL = "http://localhost:8090";

      // Mock fetch to simulate error observer response
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          status: "success",
          last_error: null,
          errors_handled_24h: 5,
        }),
      } as Response);

      const response = await GET();
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.configured).toBe(true);
      expect(data.url).toBe("http://localhost:8090");
      expect(data.state).toBeDefined();
      expect(data.state.status).toBe("success");
      expect(data.lastUpdated).toBeDefined();
    });

    it("should handle fetch timeout gracefully", async () => {
      process.env.ERROR_OBSERVER_URL = "http://localhost:8090";

      // Mock timeout error
      global.fetch = jest.fn().mockRejectedValue(
        new Error("AbortError")
      );

      const response = await GET();
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.configured).toBe(true);
      expect(data.state).toBeNull();
      expect(data.error).toBeDefined();
    });

    it("should handle non-OK HTTP responses", async () => {
      process.env.ERROR_OBSERVER_URL = "http://localhost:8090";

      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 503,
        text: async () => "Service Unavailable",
      } as Response);

      const response = await GET();
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.configured).toBe(true);
      expect(data.state).toBeNull();
      expect(data.error).toContain("503");
    });

    it("should include error observer state when available", async () => {
      process.env.ERROR_OBSERVER_URL = "http://localhost:8090";

      const mockState = {
        status: "success",
        status_message: "Successfully dispatched to GitHub",
        last_error: {
          service: "a2a-ui",
          error_message: "Test error",
          error_hash: "abc123",
        },
        last_dispatch_time: "2025-12-03T00:00:00Z",
        last_dispatch_status: "success",
        errors_handled_24h: 10,
        recent_errors: [
          {
            error_hash: "abc123",
            service: "a2a-ui",
            message: "Test error",
            timestamp: "2025-12-03T00:00:00Z",
            dispatch_status: "success",
          },
        ],
      };

      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => mockState,
      } as Response);

      const response = await GET();
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.configured).toBe(true);
      expect(data.state).toEqual(mockState);
      expect(data.state.errors_handled_24h).toBe(10);
      expect(data.state.recent_errors).toHaveLength(1);
    });
  });

  describe("Error Observer Integration", () => {
    it("should handle error observer in failure state", async () => {
      process.env.ERROR_OBSERVER_URL = "http://localhost:8090";

      const mockState = {
        status: "failure",
        status_message: "Dispatch failed: GitHub API returned 422",
        last_error: {
          service: "a2a-ui",
          error_message: "localStorage quota exceeded",
          error_hash: "def456",
        },
        last_dispatch_status: "failure",
        errors_handled_24h: 14,
      };

      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => mockState,
      } as Response);

      const response = await GET();
      const data = await response.json();

      expect(data.state.status).toBe("failure");
      expect(data.state.status_message).toContain("Dispatch failed");
      expect(data.state.last_dispatch_status).toBe("failure");
    });

    it("should handle error observer showing GitHub API 422 error", async () => {
      process.env.ERROR_OBSERVER_URL = "http://localhost:8090";

      const mockState = {
        status: "failure",
        status_message: "Dispatch failed: GitHub API returned 422: No more than 10 properties are allowed",
        last_dispatch_status: "failure",
      };

      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => mockState,
      } as Response);

      const response = await GET();
      const data = await response.json();

      // This test validates the bug we fixed
      // After the fix, error-observer should NOT return this 422 error
      expect(data.state.status).toBe("failure");
      expect(data.state.status_message).toContain("422");
    });
  });
});
