/** @type {import('jest').Config} */
const config = {
  // Use ts-jest for TypeScript support
  preset: 'ts-jest',
  
  // Test environment - use node for API routes
  testEnvironment: 'node',
  
  // Setup files to run after Jest is initialized
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  
  // Module name mapper for path aliases (matching tsconfig)
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  
  // Transform settings
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: 'tsconfig.json',
    }],
  },
  
  // Test file patterns - only match .test.ts files
  testMatch: [
    '**/__tests__/**/*.test.[jt]s?(x)',
    '**/?(*.)+(spec|test).[jt]s?(x)',
  ],
  
  // Ignore patterns
  testPathIgnorePatterns: [
    '/node_modules/',
    '/.next/',
    '/__tests__/utils/',
  ],
  
  // Coverage settings - focus on API routes for now
  collectCoverageFrom: [
    'src/app/api/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/index.ts',
  ],
  
  // Module file extensions
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  
  // Verbose output
  verbose: true,
  
  // Force exit after tests complete (handles timer issues)
  forceExit: true,
  
  // Detect open handles for debugging
  // detectOpenHandles: true,
};

module.exports = config;
