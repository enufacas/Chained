# AG-Organism Frontend - 2D Canvas Visualization
# Lightweight build serving static HTML with environment injection

FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json ./

# Install only production dependencies (express only)
RUN npm install --production

# Copy server file and public directory
COPY server.js ./
COPY public ./public

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
