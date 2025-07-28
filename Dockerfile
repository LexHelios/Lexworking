To optimize your application for deployment, here’s an example of a production-ready Dockerfile based on best practices:

```
# Use a minimal base image for production
FROM node:16-alpine AS base

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install --production

# Copy application code
COPY . .

# Expose the port your app runs on
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production

# Start the application
CMD ["npm", "start"]
```

### Key Optimizations:
1. **Use a minimal base image**: `node:16-alpine` reduces the image size and attack surface.
2. **Leverage caching**: Copy `package.json` and `package-lock.json` first to cache dependencies.
3. **Install only production dependencies**: Use `npm install --production` to exclude dev dependencies.
4. **Set environment variables**: Explicitly set `NODE_ENV=production` for optimized runtime behavior.
5. **Expose only necessary ports**: Keep the exposed ports minimal for security.

Let me know if you need further adjustments!