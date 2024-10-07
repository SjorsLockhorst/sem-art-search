# ---- Step 1: Build Phase ----
FROM node:20-slim AS build

# Define the working directory inside the container
WORKDIR /app/frontend

# Copy package.json and package-lock.json only (for caching purposes)
COPY ./frontend/package*.json ./

# Install dependencies
RUN npm install

# Prune devDependencies to reduce image size
RUN npm prune --production

# Copy the rest of the application's source code
COPY ./frontend ./

# Build the Nuxt application
RUN npm run build

# ---- Step 2: Serve Phase ----
FROM node:20-slim AS serve

# Define the work directory inside the container for the final image
WORKDIR /app/frontend

# Copy the built output from the build phase
COPY --from=build /app/frontend/.output /app/frontend/.output

# Expose port 3000 (default Nuxt.js port)
EXPOSE 3000

# Set production environment variable
ENV NODE_ENV=production

# Start Nitro server in production mode
CMD ["node", ".output/server/index.mjs"]
