#!/bin/bash

# Container and image names
CONTAINER_NAME="vpsmanager-container"
IMAGE_NAME="vpsmanager:latest"
APP_DIR="/root/projects/vpsmanager"

echo "🧹 Stopping and removing old container (if it exists)..."
docker rm -f $CONTAINER_NAME 2>/dev/null || true

echo "🏗️  Building Docker image..."
cd $APP_DIR || { echo "❌ Failed to cd to $APP_DIR"; exit 1; }
docker build -t $IMAGE_NAME .

echo "🚀 Starting new container..."
docker run -d --env-file .env -p 8971:8971 --name $CONTAINER_NAME $IMAGE_NAME

echo "✅ Container '$CONTAINER_NAME' restarted and running."
