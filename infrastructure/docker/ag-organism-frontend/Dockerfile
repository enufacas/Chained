# AG-Organism Frontend - React with react-three-fiber
# Multi-stage build for optimized production image

# Stage 1: Build React application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install all dependencies (including dev dependencies for build)
RUN npm install

# Copy application source
COPY . .

# Build React application with Vite
RUN npm run build

# Stage 2: Production server
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json ./

# Install only production dependencies
RUN npm install --production

# Copy built React app from builder stage
COPY --from=builder /app/dist ./dist

# Copy server file
COPY server.js ./

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 expressuser && \
    chown -R expressuser:nodejs /app

USER expressuser

# Expose port
EXPOSE 8080

ENV PORT=8080
ENV NODE_ENV=production

# Start server
CMD ["node", "server.js"]
