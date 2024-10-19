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

ARG NUXT_PUBLIC_API_BASE
ENV NUXT_PUBLIC_API_BASE=$NUXT_PUBLIC_API_BASE
RUN npm run generate  # This will generate static files under the `dist` folder

RUN echo "Checking if 'dist' folder was generated. See contents below:" && ls -al /app/frontend/dist

# ---- Step 2: Serve Phase ----
FROM nginx:alpine AS serve

# Copy the static site generated in the build step to the nginx html folder
COPY --from=build /app/frontend/dist /usr/share/nginx/html

# Expose port 4000
EXPOSE 4000
