#!/bin/bash
# CredentialMate Production Deployment Script
# Deploys application to AWS EC2 instance

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== CredentialMate Production Deployment ===${NC}"
echo ""

# Get EC2 IP from Terraform
echo -e "${YELLOW}→ Getting EC2 instance IP...${NC}"
cd terraform
EC2_IP=$(terraform output -raw ec2_public_ip 2>/dev/null || echo "")
cd ..

if [ -z "$EC2_IP" ]; then
    echo -e "${RED}✗ Could not get EC2 IP from Terraform${NC}"
    echo "Please run: cd terraform && terraform output ec2_public_ip"
    exit 1
fi

echo -e "${GREEN}✓ EC2 IP: ${EC2_IP}${NC}"

# Get secrets from terraform.tfvars
echo -e "${YELLOW}→ Reading secrets from terraform.tfvars...${NC}"
DB_PASSWORD=$(grep 'db_password' terraform/terraform.tfvars | cut -d'"' -f2)
APP_SECRET=$(grep 'app_secret_key' terraform/terraform.tfvars | cut -d'"' -f2)
JWT_SECRET=$(grep 'jwt_secret_key' terraform/terraform.tfvars | cut -d'"' -f2)
ENCRYPTION_KEY=$(grep 'encryption_key' terraform/terraform.tfvars | cut -d'"' -f2)

# Get AWS credentials from .env
AWS_ACCESS_KEY_ID=$(grep 'AWS_ACCESS_KEY_ID=' .env | cut -d'=' -f2)
AWS_SECRET_ACCESS_KEY=$(grep 'AWS_SECRET_ACCESS_KEY=' .env | cut -d'=' -f2)

# Create production .env file
echo -e "${YELLOW}→ Creating production .env file...${NC}"
cat > .env.prod.tmp <<EOF
# Production Environment - Auto-generated $(date)
DATABASE_URL=postgresql://credentialmate:${DB_PASSWORD}@credentialmate-production-db.cm1ksgqm0c00.us-east-1.rds.amazonaws.com:5432/credentialmate
SECRET_KEY=${APP_SECRET}
JWT_SECRET_KEY=${JWT_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
S3_BUCKET_NAME=credentialmate-production-documents
ENVIRONMENT=production
DEBUG=false
DOCKER_CONTAINER=true
CORS_ORIGINS=https://credentialmate.com,https://www.credentialmate.com
USE_MOCK_DOCUMENT_PARSER=false
EMAIL_ENABLED=true
REDIS_URL=redis://redis:6379
EOF

echo -e "${GREEN}✓ Production .env file created${NC}"

# Create deployment package
echo -e "${YELLOW}→ Creating deployment package...${NC}"
tar -czf deploy-package.tar.gz \
    backend/ \
    frontend/ \
    docker-compose.prod.yml \
    .env.prod.tmp \
    --exclude='backend/__pycache__' \
    --exclude='backend/.pytest_cache' \
    --exclude='backend/uploads/*' \
    --exclude='frontend/node_modules' \
    --exclude='frontend/.next'

echo -e "${GREEN}✓ Deployment package created${NC}"

# SSH key configuration
SSH_KEY="$HOME/.ssh/credentialmate-prod-key-2025.pem"
SSH_OPTS="-i ${SSH_KEY} -o StrictHostKeyChecking=no"

# Copy to EC2
echo -e "${YELLOW}→ Copying deployment package to EC2...${NC}"
scp ${SSH_OPTS} deploy-package.tar.gz ec2-user@${EC2_IP}:/tmp/

# Deploy on EC2
echo -e "${YELLOW}→ Deploying application on EC2...${NC}"
ssh ${SSH_OPTS} ec2-user@${EC2_IP} << 'ENDSSH'
set -e

echo "=== On EC2 Instance ==="

# Create application directory
sudo mkdir -p /opt/credentialmate
cd /opt/credentialmate

# Extract deployment package
echo "→ Extracting deployment package..."
sudo tar -xzf /tmp/deploy-package.tar.gz -C /opt/credentialmate
sudo mv .env.prod.tmp .env
sudo chown -R ec2-user:ec2-user /opt/credentialmate

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "→ Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Build and start containers
echo "→ Building Docker images..."
sudo docker-compose -f docker-compose.prod.yml build --no-cache

echo "→ Starting containers..."
sudo docker-compose -f docker-compose.prod.yml up -d

# Wait for backend to be healthy
echo "→ Waiting for backend to be ready..."
for i in {1..30}; do
    if sudo docker-compose -f docker-compose.prod.yml exec -T backend curl -f http://localhost:8000/api/health 2>/dev/null; then
        echo "✓ Backend is healthy!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Run database migrations
echo "→ Running database migrations..."
sudo docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

# Seed production data
echo "→ Seeding production data..."
sudo docker-compose -f docker-compose.prod.yml exec -T backend python -m app.scripts.seed_all_data

echo "✓ Deployment complete!"
echo ""
echo "Application Status:"
sudo docker-compose -f docker-compose.prod.yml ps

ENDSSH

# Cleanup
echo -e "${YELLOW}→ Cleaning up...${NC}"
rm -f deploy-package.tar.gz .env.prod.tmp

echo ""
echo -e "${GREEN}=== Deployment Complete! ===${NC}"
echo ""
echo "Application URLs:"
echo "  - Frontend: http://${EC2_IP}:3000"
echo "  - Backend API: http://${EC2_IP}:8000"
echo "  - API Docs: http://${EC2_IP}:8000/docs"
echo "  - Health Check: http://${EC2_IP}:8000/api/health"
echo ""
echo "ALB URL (will work once DNS propagates):"
echo "  - https://credentialmate.com"
echo ""
echo "To view logs:"
echo "  ssh ec2-user@${EC2_IP}"
echo "  cd /opt/credentialmate"
echo "  sudo docker-compose -f docker-compose.prod.yml logs -f"
echo ""
