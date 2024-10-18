# ---- Step 1: Build Phase ----
FROM node:20-slim AS build

# Define the working directory inside the container
WORKDIR /app/frontend

# Copy package.json and package-lock.json only (for caching purposes)
COPY ./frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application's source code
COPY ./frontend ./

# Generate static files (SSG)
RUN npm run generate  # This will generate static files under the `dist` folder

# ---- Step 2: Serve Phase ----
FROM nginx:alpine AS serve

# Copy the static site generated in the build step to the nginx html folder
COPY --from=build /app/frontend/dist /usr/share/nginx/html
