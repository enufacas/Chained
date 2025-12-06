# AG-Organism Frontend
# Serves ag-organism.html with environment variable injection

FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install --production

# Copy application files
COPY server.js ./
COPY public ./public

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 expressuser

USER expressuser

# Expose port
EXPOSE 8080

ENV PORT=8080
ENV NODE_ENV=production

# Start server
CMD ["node", "server.js"]
