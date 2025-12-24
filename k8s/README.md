# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying iPhone Export to a k3s cluster.

## Prerequisites

- Kubernetes cluster (k3s recommended)
- kubectl configured to access the cluster
- GitHub Container Registry access (for pulling images)
- Secrets configured (see `secrets-template.yaml`)

## Deployment Steps

### 1. Create Namespace

```bash
kubectl apply -f namespace.yaml
```

### 2. Create Secrets

Copy `secrets-template.yaml` to `secrets.yaml` and fill in all values:

```bash
cp secrets-template.yaml secrets.yaml
# Edit secrets.yaml with your actual values
kubectl apply -f secrets.yaml
```

**Important:** Never commit `secrets.yaml` to git!

### 3. Create Persistent Volume Claim

```bash
kubectl apply -f postgres-pvc.yaml
```

### 4. Deploy Database and Redis

```bash
kubectl apply -f postgres-deployment.yaml
kubectl apply -f redis-deployment.yaml
```

Wait for these to be ready:

```bash
kubectl wait --for=condition=ready pod -l app=iphone-export,component=postgres -n iphone-export --timeout=300s
kubectl wait --for=condition=ready pod -l app=iphone-export,component=redis -n iphone-export --timeout=300s
```

### 5. Initialize Database

Run the database initialization script:

```bash
# Get a pod name
POD_NAME=$(kubectl get pods -n iphone-export -l app=iphone-export,component=api -o jsonpath='{.items[0].metadata.name}')

# Run init script
kubectl exec -n iphone-export $POD_NAME -- python backend/init_db.py
```

### 6. Deploy API and Frontend

```bash
kubectl apply -f api-deployment.yaml
kubectl apply -f frontend-deployment.yaml
```

### 7. Configure Ingress

Update `ingress.yaml` with your domain name, then apply:

```bash
kubectl apply -f ingress.yaml
```

### 8. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n iphone-export

# Check services
kubectl get svc -n iphone-export

# Check ingress
kubectl get ingress -n iphone-export
```

## Updating the Deployment

### Update API Image

```bash
# Update the image tag in api-deployment.yaml, then:
kubectl apply -f api-deployment.yaml
kubectl rollout restart deployment/iphone-export-api -n iphone-export
```

### Update Frontend Image

```bash
# Update the image tag in frontend-deployment.yaml, then:
kubectl apply -f frontend-deployment.yaml
kubectl rollout restart deployment/iphone-export-frontend -n iphone-export
```

## Troubleshooting

### View Logs

```bash
# API logs
kubectl logs -n iphone-export -l app=iphone-export,component=api --tail=100

# Frontend logs
kubectl logs -n iphone-export -l app=iphone-export,component=frontend --tail=100

# Database logs
kubectl logs -n iphone-export -l app=iphone-export,component=postgres --tail=100
```

### Check Pod Status

```bash
kubectl describe pod <pod-name> -n iphone-export
```

### Access Database

```bash
# Get postgres pod
POD_NAME=$(kubectl get pods -n iphone-export -l app=iphone-export,component=postgres -o jsonpath='{.items[0].metadata.name}')

# Connect to database
kubectl exec -it -n iphone-export $POD_NAME -- psql -U postgres -d iphone_export
```

## Resource Limits

The deployments are configured with resource limits optimized for Raspberry Pi:

- **PostgreSQL**: 256Mi-512Mi memory, 100m-500m CPU
- **Redis**: 128Mi-256Mi memory, 50m-200m CPU
- **API**: 512Mi-1Gi memory, 200m-1000m CPU
- **Frontend**: 128Mi-256Mi memory, 100m-500m CPU

Adjust these in the deployment files if needed for your cluster.

## Backup

### Database Backup

```bash
# Get postgres pod
POD_NAME=$(kubectl get pods -n iphone-export -l app=iphone-export,component=postgres -o jsonpath='{.items[0].metadata.name}')

# Create backup
kubectl exec -n iphone-export $POD_NAME -- pg_dump -U postgres iphone_export > backup-$(date +%Y%m%d).sql
```

### Restore Database

```bash
# Get postgres pod
POD_NAME=$(kubectl get pods -n iphone-export -l app=iphone-export,component=postgres -o jsonpath='{.items[0].metadata.name}')

# Restore backup
kubectl exec -i -n iphone-export $POD_NAME -- psql -U postgres iphone_export < backup-YYYYMMDD.sql
```




