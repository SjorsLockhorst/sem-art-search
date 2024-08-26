FROM node:18

# Set the working directory
WORKDIR /app/frontend

# Copy package.json and package-lock.json
COPY ./frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY ./frontend .

# Expose the port Nuxt runs on
EXPOSE 3000

# Command to run the Nuxt app with hot reload
CMD ["npm", "run", "dev"]
