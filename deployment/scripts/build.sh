#!/bin/bash

echo "Building Docker images..."

docker-compose -f deployment/docker/docker-compose.yml build

echo "Build completed."