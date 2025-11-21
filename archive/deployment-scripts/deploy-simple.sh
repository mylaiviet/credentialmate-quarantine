#!/bin/bash
# Simplified CredentialMate Production Deployment
# Uses rsync for efficient file transfer

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== CredentialMate Production Deployment ===${NC}"
echo ""

# Get EC2 IP
echo -e "${YELLOW}→ Getting EC2 instance IP...${NC}"
cd terraform
EC2_IP=$(terraform output -raw ec2_public_ip 2>/dev/null || echo "")
cd ..

if [ -z "$EC2_IP" ]; then
    echo -e "${RED}✗ Could not get EC2 IP${NC}"
    exit 1
fi

echo -e "${GREEN}✓ EC2 IP: ${EC2_IP}${NC}"

# Get secrets
echo -e "${YELLOW}→ Reading secrets...${NC}"
DB_PASSWORD=$(grep 'db_password' terraform/terraform.tfvars | cut -d'"' -f2)
APP_SECRET=$(grep 'app_secret_key' terraform/terraform.tfvars | cut -d'"' -f2)
JWT_SECRET=$(grep 'jwt_secret_key' terraform/terraform.tfvars | cut -d'"' -f2)
ENCRYPTION_KEY=$(grep 'encryption_key' terraform/terraform.tfvars | cut -d'"' -f2)
AWS_ACCESS_KEY_ID=$(grep 'AWS_ACCESS_KEY_ID=' .env | cut -d'=' -f2)
AWS_SECRET_ACCESS_KEY=$(grep 'AWS_SECRET_ACCESS_KEY=' .env | cut -d'=' -f2)

# Create production .env
echo -e "${YELLOW}→ Creating production .env...${NC}"
cat > .env.prod <<EOF
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

echo -e "${GREEN}✓ Production .env created${NC}"

# SSH key configuration
SSH_KEY="$HOME/.ssh/credentialmate-prod-key-2025.pem"
SSH_OPTS="-i ${SSH_KEY} -o StrictHostKeyChecking=no"

# Copy files to EC2
echo -e "${YELLOW}→ Copying files to EC2...${NC}"

# Copy docker-compose
scp ${SSH_OPTS} docker-compose.prod.yml ec2-user@${EC2_IP}:/tmp/

# Copy .env
scp ${SSH_OPTS} .env.prod ec2-user@${EC2_IP}:/tmp/

# Copy backend source (excluding unnecessary files)
echo -e "${YELLOW}→ Syncing backend code...${NC}"
rsync -av --delete \
    -e "ssh ${SSH_OPTS}" \
    --exclude='__pycache__' \
    --exclude='.pytest_cache' \
    --exclude='uploads' \
    --exclude='*.pyc' \
    --exclude='.env' \
    backend/ ec2-user@${EC2_IP}:/tmp/backend/

# Copy frontend source (excluding build artifacts)
echo -e "${YELLOW}→ Syncing frontend code...${NC}"
rsync -av --delete \
    -e "ssh ${SSH_OPTS}" \
    --exclude='node_modules' \
    --exclude='.next' \
    --exclude='.env' \
    frontend/ ec2-user@${EC2_IP}:/tmp/frontend/

echo -e "${GREEN}✓ Files copied to EC2${NC}"

# Deploy on EC2
echo -e "${YELLOW}→ Deploying on EC2...${NC}"
ssh ${SSH_OPTS} ec2-user@${EC2_IP} << 'ENDSSH'
set -e

echo "=== On EC2 Instance ==="

# Create app directory
sudo mkdir -p /opt/credentialmate
cd /opt/credentialmate

# Move files
sudo mv /tmp/docker-compose.prod.yml ./
sudo mv /tmp/.env.prod .env
sudo rm -rf backend frontend
sudo mv /tmp/backend ./
sudo mv /tmp/frontend ./

sudo chown -R ec2-user:ec2-user /opt/credentialmate

# Install Docker Compose if needed
if ! command -v docker-compose &> /dev/null; then
    echo "→ Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Build and start
echo "→ Building Docker images..."
sudo docker-compose -f docker-compose.prod.yml build --no-cache

echo "→ Starting containers..."
sudo docker-compose -f docker-compose.prod.yml up -d

# Wait for backend
echo "→ Waiting for backend..."
for i in {1..30}; do
    if sudo docker-compose -f docker-compose.prod.yml exec -T backend curl -f http://localhost:8000/api/health 2>/dev/null; then
        echo "✓ Backend is healthy!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Run migrations
echo "→ Running database migrations..."
sudo docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

# Seed data
echo "→ Seeding production data..."
sudo docker-compose -f docker-compose.prod.yml exec -T backend python -m app.scripts.seed_all_data

echo "✓ Deployment complete!"
echo ""
echo "Application Status:"
sudo docker-compose -f docker-compose.prod.yml ps

ENDSSH

# Cleanup
rm -f .env.prod

echo ""
echo -e "${GREEN}=== Deployment Complete! ===${NC}"
echo ""
echo "Application URLs:"
echo "  - Frontend: http://${EC2_IP}:3000"
echo "  - Backend API: http://${EC2_IP}:8000"
echo "  - API Docs: http://${EC2_IP}:8000/docs"
echo "  - Health Check: http://${EC2_IP}:8000/api/health"
echo ""
echo "To view logs:"
echo "  ssh ec2-user@${EC2_IP}"
echo "  cd /opt/credentialmate"
echo "  sudo docker-compose -f docker-compose.prod.yml logs -f"
echo ""
