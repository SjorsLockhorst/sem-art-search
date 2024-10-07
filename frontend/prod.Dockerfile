FROM node:18

WORKDIR /app/frontend

COPY ./frontend/package*.json ./

RUN npm install --omit=dev

COPY ./frontend .

# Build your Nuxt application for production
RUN npm run build 

# Expose port 3000 (default Nuxt.js port)
EXPOSE 3000

# The environment variable for Nuxt to detect it's in production mode
ENV NODE_ENV=production

# Start Nitro server in production mode
CMD ["node", ".output/server/index.mjs"]
