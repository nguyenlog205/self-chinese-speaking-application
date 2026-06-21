#!/bin/bash

echo "Starting deployment..."

docker-compose -f deployment/docker/docker-compose.yml up -d

echo "Deployment completed. Services running at:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"