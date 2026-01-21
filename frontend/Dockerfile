FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/package.json ./
COPY frontend/package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY frontend .

# Build application
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy built application
COPY --from=builder /app/next.config.js ./
# Create public directory and copy contents (handles empty dir)
RUN mkdir -p ./public
COPY --from=builder /app/public/ ./public/
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Use non-root user
RUN chown -R node:node /app
USER node

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Run application
CMD ["npm", "start"]





