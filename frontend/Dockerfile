# Stage 1: Build
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Runtime
FROM node:18-alpine

WORKDIR /app

# Install serve to run the application
RUN npm install -g serve

# Copy built files from builder
COPY --from=build /app/dist ./dist

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Serve the application
CMD ["serve", "-s", "dist", "-l", "3000"]
