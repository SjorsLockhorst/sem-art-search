# ---- Step 1: Build Phase ----
FROM oven/bun:alpine AS base
WORKDIR /usr/src/app

FROM base AS install

RUN mkdir -p /temp/prod
COPY ./frontend/package.json ./frontend/bun.lockb /temp/prod/
RUN cd /temp/prod && bun install --frozen-lockfile --production --verbose --concurrent-scripts 1

FROM base AS build
COPY --from=install /temp/prod/node_modules node_modules

ARG NUXT_PUBLIC_API_BASE
ENV NUXT_PUBLIC_API_BASE=$NUXT_PUBLIC_API_BASE
ENV NODE_ENV=production

COPY ./frontend ./

RUN bun --bun --smol run generate 

# ---- Step 2: Serve Phase ----
FROM nginx:alpine AS serve

# Copy the static site generated in the build step to the nginx html folder
COPY --from=build /usr/src/app/dist /usr/share/nginx/html

# Expose port 4000
EXPOSE 4000
