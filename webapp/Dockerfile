# Frontend Dockerfile (Nuxt with pnpm)
FROM node:20-alpine AS base

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy application code
COPY . .

# Build the application
RUN pnpm run build

# Production stage
FROM node:20-alpine AS production

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy built application
COPY --from=base /app/.output /app/.output
COPY --from=base /app/package.json /app/package.json

# Expose port
EXPOSE 3000

# Set environment variable
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

# Run the application
CMD ["node", ".output/server/index.mjs"]
