#!/bin/bash
set -e

# VPS deployment script for HoffMagic blog
# This script deploys the application to a Virtual Private Server

# Configuration variables
SERVER_USER="username"
SERVER_IP="your.server.ip"
DEPLOY_DIR="/opt/hoffmagic"

echo "Deploying hoffmagic to VPS..."

# Build the application
echo "Building application..."
docker-compose build

# Create deployment archive
echo "Creating deployment archive..."
git archive --format=tar.gz -o deploy.tar.gz HEAD

# Copy files to server
echo "Copying files to server..."
scp deploy.tar.gz $SERVER_USER@$SERVER_IP:/tmp/

# Execute remote deployment commands
echo "Executing remote deployment commands..."
ssh $SERVER_USER@$SERVER_IP << ENDSSH
  # Create deployment directory if it doesn't exist
  mkdir -p $DEPLOY_DIR
  
  # Extract archive
  tar -xzf /tmp/deploy.tar.gz -C $DEPLOY_DIR
  
  # Set up environment file
  cat > $DEPLOY_DIR/.env << EOF
DATABASE_URL=postgresql+psycopg://hoffmagic:hoffmagic@localhost:5432/hoffmagic
SECRET_KEY=$(openssl rand -hex 32)
# Ensure JSON array format for allowed hosts
ALLOWED_HOSTS='["'$SERVER_IP'", "localhost", "127.0.0.1"]'
DEBUG=false
EOF
  
  # Start the application with Docker Compose
  cd $DEPLOY_DIR
  docker-compose up -d
  
  # Clean up
  rm /tmp/deploy.tar.gz
ENDSSH

# Clean up local archive
rm deploy.tar.gz

echo "Deployment completed successfully!"
