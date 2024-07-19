# Base image for Python
FROM python:3.9 AS python-base

# Set the working directory for Python
WORKDIR /project/admin-panel

# Copy the requirements file
COPY /project/admin-panel/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the Python code
COPY /project/admin-panel/ .

# Base image for Node.js
FROM node:14 AS node-base

# Set the working directory for Node.js
WORKDIR /project/admin-panel/my-app

# Copy the package.json and package-lock.json
COPY /project/admin-panel/my-app/package*.json ./

# Install Node.js dependencies
RUN npm install

# Copy the rest of the Node.js code
COPY project/admin-panel/my-app/ .

# Final stage for combining Python and Node.js services
FROM python:3.9-slim

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
