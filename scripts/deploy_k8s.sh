#!/bin/bash
set -e

# Kubernetes deployment script for HoffMagic blog
# This script deploys the application to a Kubernetes cluster (OVH Cloud)

# Configuration variables
IMAGE_TAG=$(git rev-parse --short HEAD)
DOCKER_REGISTRY="your-registry.ovh.com"
NAMESPACE="hoffmagic"

echo "Deploying hoffmagic to Kubernetes..."

# Build and push Docker image
echo "Building and pushing Docker image..."
docker build -t $DOCKER_REGISTRY/hoffmagic:$IMAGE_TAG .
docker push $DOCKER_REGISTRY/hoffmagic:$IMAGE_TAG

# Create namespace if it doesn't exist
kubectl get namespace $NAMESPACE >/dev/null 2>&1 || kubectl create namespace $NAMESPACE

# Apply Kubernetes manifests with proper image tag
echo "Applying Kubernetes manifests..."
cat k8s/deployment.yaml | sed "s|\${DOCKER_REGISTRY}|$DOCKER_REGISTRY|g" | sed "s|\${IMAGE_TAG}|$IMAGE_TAG|g" | kubectl apply -f - -n $NAMESPACE
kubectl apply -f k8s/service.yaml -n $NAMESPACE
kubectl apply -f k8s/configmap.yaml -n $NAMESPACE

echo "Deployment completed successfully!"
