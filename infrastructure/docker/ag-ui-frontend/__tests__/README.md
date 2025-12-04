# AG-UI Frontend Tests

This directory contains the test suite for the AG-UI Frontend application.

## Test Framework

- **Jest**: JavaScript testing framework
- **ts-jest**: TypeScript support for Jest
- **@testing-library/jest-dom**: Custom Jest matchers for DOM testing

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode (re-runs on file changes)
npm run test:watch

# Run tests with coverage report
npm run test:coverage
```

## Test Structure

```
__tests__/
├── api/
│   ├── agent.test.ts      # Tests for /api/agent endpoint
│   ├── pipeline.test.ts   # Tests for /api/pipeline endpoint
│   ├── team.test.ts       # Tests for /api/team endpoint
│   ├── activity.test.ts   # Tests for /api/activity endpoint
│   ├── error-observer.test.ts # Tests for /api/error-observer endpoint
│   └── registry.test.ts   # Tests for /api/registry endpoint
├── components/
│   └── ErrorBoundary.test.tsx  # Tests for ErrorBoundary component
├── lib/
│   ├── storage.test.ts    # Tests for storage utilities
│   ├── storage-cleanup.test.ts # Tests for storage cleanup
│   ├── storage-metadata-stripping.test.ts # Tests for metadata handling
│   ├── storage-session-artifacts.test.ts # Tests for session artifacts
│   └── storage-session-timestamp.test.ts # Tests for timestamp preservation
├── e2e/
│   └── custom-team-e2e.test.ts # End-to-end tests for team workflows
├── utils/
│   └── testUtils.ts       # Shared test utilities
└── README.md              # This file
```

## API Tests

### Agent API (`/api/agent`)

Tests for **Feature 2: Direct Agent Interaction**

| Test | Description |
|------|-------------|
| GET returns agent list | Verifies the endpoint returns all available agents |
| Agent fields are complete | Ensures each agent has name, displayName, icon, etc. |
| @agent-name parsing | Tests that @research-agent, @seo-agent, @writer-agent work |
| Help response | Returns usage help when no agent is mentioned |
| Unknown agent | Returns 404 for non-existent agents |
| Missing message | Returns 400 when message is not provided |

### Pipeline API (`/api/pipeline`)

Tests for **Feature 1: Pipeline Creation** and **Feature 3: Real-Time Status**

| Test | Description |
|------|-------------|
| Create pipeline | POST creates a new pipeline with unique ID |
| Validation | Returns 400 for missing or empty topic |
| List pipelines | GET returns list with filtering options |
| Get by ID | GET with ID returns specific pipeline |
| Completed data | Includes previously completed pipelines |
| Data structure | Validates all required fields are present |

## Component Tests

### ErrorBoundary Component

Tests for error boundary that catches React component errors:

| Test | Description |
|------|-------------|
| Renders children normally | Verifies children render when no error occurs |
| Catches errors | Shows fallback UI when child component throws |
| Custom fallback | Uses custom fallback UI when provided |
| Error callback | Calls onError callback when error is caught |
| HOC pattern | Tests withErrorBoundary higher-order component |
| Error logging | Verifies errors are logged to console and backend |

## Writing New Tests

### Testing API Routes

```typescript
import { NextRequest } from 'next/server';

describe('Your API (/api/your-endpoint)', () => {
  const createMockRequest = (method: string, body?: object): NextRequest => {
    return new Request('http://localhost:3000/api/your-endpoint', {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    }) as unknown as NextRequest;
  };

  it('should do something', async () => {
    const { GET, POST } = await import('@/app/api/your-endpoint/route');
    
    const request = createMockRequest('POST', { data: 'value' });
    const response = await POST(request);
    const data = await response.json();
    
    expect(response.status).toBe(200);
    expect(data.success).toBe(true);
  });
});
```

### Testing React Components

```typescript
/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import YourComponent from '@/components/YourComponent';

describe('YourComponent', () => {
  // Mock console.error if testing error boundaries
  const originalError = console.error;
  beforeAll(() => {
    console.error = jest.fn();
  });
  afterAll(() => {
    console.error = originalError;
  });

  it('should render with props', () => {
    render(<YourComponent prop="value" />);
    
    expect(screen.getByText('value')).toBeInTheDocument();
  });

  it('should handle user interaction', () => {
    render(<YourComponent />);
    
    const button = screen.getByRole('button', { name: /click me/i });
    fireEvent.click(button);
    
    expect(screen.getByText('Clicked!')).toBeInTheDocument();
  });
});
```

**Important:** Use `@jest-environment jsdom` at the top of component test files to enable DOM APIs (window, document, etc.).

### Using Test Utilities

```typescript
import { 
  createAgentRequest, 
  createPipelineRequest,
  VALID_AGENTS,
  VALID_PIPELINE_STATUSES 
} from '../utils/testUtils';

it('should use utilities', async () => {
  const request = createAgentRequest('POST', { message: '@research-agent test' });
  // ... test logic
});
```

## Coverage

Run `npm run test:coverage` to generate a coverage report. The report will be available in the `coverage/` directory.

### Current Coverage Targets

- Statements: 80%
- Branches: 75%
- Functions: 80%
- Lines: 80%

## Debugging Tests

### Run a single test file

```bash
npx jest __tests__/api/agent.test.ts
```

### Run tests matching a pattern

```bash
npx jest --testNamePattern="should parse @research-agent"
```

### Verbose output

```bash
npx jest --verbose
```

### Detect open handles (for debugging timeouts)

```bash
npx jest --detectOpenHandles
```

## Notes

- Tests use dynamic imports (`await import('@/app/api/...')`) to work around Next.js module resolution
- Pipeline tests may trigger timers due to async progress updates; this is expected
- The `jest.setup.ts` file extends Jest with DOM matchers and global mocks
