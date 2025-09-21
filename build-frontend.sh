#!/bin/bash

# Frontend build script for deployment
set -e

echo "Starting frontend build process..."

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "Installing dependencies..."
npm ci

# Run type checking
echo "Running type check..."
npm run type-check

# Build the project
echo "Building frontend..."
npm run build

echo "Frontend build completed successfully!"