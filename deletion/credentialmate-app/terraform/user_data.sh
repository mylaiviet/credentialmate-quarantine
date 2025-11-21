#!/bin/bash
# ============================================
# EC2 User Data Script
# CredentialMate - Application Server Initialization
# ============================================

set -e

# Update system
echo "Updating system packages..."
yum update -y

# Install Docker
echo "Installing Docker..."
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

# Install Docker Compose
echo "Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Install Git
echo "Installing Git..."
yum install -y git

# Install AWS CLI v2
echo "Installing AWS CLI..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

# Install CloudWatch Agent
echo "Installing CloudWatch Agent..."
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm
rm amazon-cloudwatch-agent.rpm

# Create application directory
echo "Creating application directory..."
mkdir -p /opt/credentialmate
cd /opt/credentialmate

# Create CloudWatch agent configuration
echo "Configuring CloudWatch agent..."
cat > /opt/aws/amazon-cloudwatch-agent/etc/config.json <<'EOF'
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/credentialmate/app.log",
            "log_group_name": "/aws/${project_name}/${environment}/application",
            "log_stream_name": "{instance_id}/app.log"
          },
          {
            "file_path": "/var/log/docker",
            "log_group_name": "/aws/${project_name}/${environment}/docker",
            "log_stream_name": "{instance_id}/docker.log"
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "CredentialMate/${environment}",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          {
            "name": "cpu_usage_idle",
            "rename": "CPU_IDLE",
            "unit": "Percent"
          },
          "cpu_usage_iowait"
        ],
        "metrics_collection_interval": 60,
        "totalcpu": false
      },
      "disk": {
        "measurement": [
          {
            "name": "used_percent",
            "rename": "DISK_USED",
            "unit": "Percent"
          }
        ],
        "metrics_collection_interval": 60,
        "resources": [
          "*"
        ]
      },
      "diskio": {
        "measurement": [
          "io_time"
        ],
        "metrics_collection_interval": 60
      },
      "mem": {
        "measurement": [
          {
            "name": "mem_used_percent",
            "rename": "MEM_USED",
            "unit": "Percent"
          }
        ],
        "metrics_collection_interval": 60
      }
    }
  }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json

# Create log directory
mkdir -p /var/log/credentialmate

# Set up deployment script (will be called by CI/CD)
cat > /opt/credentialmate/deploy.sh <<'DEPLOY_SCRIPT'
#!/bin/bash
set -e

echo "Starting deployment..."

# Get secrets from AWS Secrets Manager
export AWS_REGION=${aws_region}
export DATABASE_URL=$(aws secretsmanager get-secret-value --secret-id ${project_name}/${environment}/database --query SecretString --output text | jq -r '.connection_string')
export SECRET_KEY=$(aws secretsmanager get-secret-value --secret-id ${project_name}/${environment}/app --query SecretString --output text | jq -r '.secret_key')
export JWT_SECRET_KEY=$(aws secretsmanager get-secret-value --secret-id ${project_name}/${environment}/app --query SecretString --output text | jq -r '.jwt_secret_key')
export ENCRYPTION_KEY=$(aws secretsmanager get-secret-value --secret-id ${project_name}/${environment}/app --query SecretString --output text | jq -r '.encryption_key')

# Pull latest code
cd /opt/credentialmate
git pull origin main

# Build and start containers
docker-compose down
docker-compose up -d --build

# Run database migrations
docker-compose exec -T backend alembic upgrade head

# Optional: Run seed data on first deployment
if [ "$1" == "--seed" ]; then
  echo "Running seed data..."
  docker-compose exec -T backend python -m app.scripts.seed_all_data
fi

echo "Deployment complete!"
DEPLOY_SCRIPT

chmod +x /opt/credentialmate/deploy.sh

echo "EC2 initialization complete!"
