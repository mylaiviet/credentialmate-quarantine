#!/bin/bash
# CredentialMate Production Deployment Script
# Session: 20251109-174043
# Runs on EC2 instance to deploy the full application

set -e

echo "============================================"
echo "CredentialMate Production Deployment"
echo "Started at: $(date)"
echo "============================================"

# Step 1: Configure Let's Encrypt SSL
echo "[1/6] Setting up Let's Encrypt SSL..."
sudo certbot --nginx -d credentialmate.com -d www.credentialmate.com --non-interactive --agree-tos --email admin@credentialmate.com --redirect

# Step 2: Clone repository (using current directory files - will be uploaded)
echo "[2/6] Setting up application directory..."
cd /opt/credentialmate

# Step 3: Create production docker-compose.yml
echo "[3/6] Creating production docker-compose configuration..."
cat > docker-compose.prod.yml <<'EOF'
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: credentialmate-backend-prod
    restart: always
    env_file:
      - backend.env
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - credentialmate-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: credentialmate-frontend-prod
    restart: always
    env_file:
      - frontend.env
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - credentialmate-network

networks:
  credentialmate-network:
    driver: bridge
EOF

# Step 4: Create frontend Dockerfile if missing
echo "[4/6] Creating frontend Dockerfile..."
cat > frontend/Dockerfile.prod <<'EOF'
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/package*.json ./
COPY --from=build /app/next.config.js ./
RUN npm ci --only=production
EXPOSE 3000
CMD ["npm", "start"]
EOF

# Step 5: Run database migrations
echo "[5/6] Running database migrations..."
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
source /opt/credentialmate/backend.env
alembic upgrade head
deactivate
cd ..

# Step 6: Build and start containers
echo "[6/6] Building and starting Docker containers..."
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Configure Nginx to proxy to containers
echo "Updating Nginx configuration..."
sudo cat > /etc/nginx/sites-available/credentialmate <<'NGINX_CONFIG'
server {
    listen 80;
    server_name credentialmate.com www.credentialmate.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name credentialmate.com www.credentialmate.com;

    ssl_certificate /etc/letsencrypt/live/credentialmate.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/credentialmate.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
NGINX_CONFIG

sudo nginx -t
sudo systemctl reload nginx

echo "============================================"
echo "Deployment Complete!"
echo "Application should be available at:"
echo "  https://credentialmate.com"
echo "============================================"

# Show container status
docker-compose -f docker-compose.prod.yml ps
