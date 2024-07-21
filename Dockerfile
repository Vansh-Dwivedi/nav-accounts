# Stage 1: Base image for Python
FROM python:3.9 AS python-base

# Set the working directory for Python
WORKDIR /project/admin-panel

# Copy the requirements file first to leverage Docker cache
COPY project/admin-panel/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the Python code
COPY project/admin-panel/ .

# Stage 2: Base image for Node.js
FROM node:14 AS node-base

# Set the working directory for Node.js
WORKDIR /project/admin-panel/my-app

# Copy the package.json and package-lock.json first to leverage Docker cache
COPY project/admin-panel/my-app/package*.json ./

# Install Node.js dependencies
RUN npm install

# Copy the rest of the Node.js code
COPY project/admin-panel/my-app/ .

# Final stage: Combine Python and Node.js environments
FROM python:3.9-slim

# Install Node.js in the final image
RUN apt-get update && apt-get install -y curl gnupg && curl -sL https://deb.nodesource.com/setup_14.x | bash - && apt-get install -y nodejs

# Install Flask
RUN pip install Flask

# Set the working directory
WORKDIR /project

# Copy the built Python environment
COPY --from=python-base /project/admin-panel /project/admin-panel

# Copy the built Node.js environment
COPY --from=node-base /project/admin-panel/my-app /project/admin-panel/my-app

# Expose the necessary ports
EXPOSE 7850 5000 3000

# Run the Python HTTP server, Flask server, and Node.js application
CMD ["sh", "-c", "cd /project/admin-panel && python -m http.server 7850 & flask run --host=0.0.0.0 --port=5000 & cd /project/admin-panel/my-app && npm start"]
