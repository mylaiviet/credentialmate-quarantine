# 20251120 AWS Deploy v1

## Deployment Summary

**Date:** November 20, 2025
**Target:** CredentialMate production deployment to AWS
**Architecture:** EC2 + RDS PostgreSQL + S3 + Let's Encrypt SSL (no ALB, no NAT Gateway)
**Domain:** https://credentialmate.com

---

## Deployment Approach

This deployment used a simplified architecture to minimize costs:
- Single EC2 instance (t3.micro) running Docker containers
- RDS PostgreSQL (db.t4g.micro) for database
- VPC Endpoints for SSM instead of NAT Gateway
- Let's Encrypt/Certbot for SSL certificates
- Elastic IP for static public IP

---

## Issues Encountered and Fixes

### 1. EC2 Root Volume Size Too Small (2GB Default)

**Issue:** Default AL2023 AMI creates only 2GB root volume, insufficient for Docker images.

**Symptom:**
```
no space left on device
```

**Root Cause:** Docker images for backend, frontend, nginx, postgres, and redis exceed 2GB when built.

**Fix Applied:** Added `block_device_mappings` to launch template in `terraform/ec2.tf`:
```hcl
block_device_mappings {
  device_name = "/dev/xvda"
  ebs {
    volume_size           = 20
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true
  }
}
```

**Location:** [terraform/ec2.tf](../terraform/ec2.tf) lines 216-225

---

### 2. OOM Killer Terminates Docker Builds

**Issue:** t3.micro has only 1GB RAM (actually ~911MB usable), insufficient for building Docker images in parallel.

**Symptom:**
```
signal: killed
```

**Root Cause:** OOM (Out of Memory) killer terminates docker-buildx process during multi-stage builds.

**Fix Applied:** Added swap file creation to `terraform/user_data.sh`:
```bash
# Create swap file (needed for Docker builds on t3.micro)
echo "Creating 2GB swap file..."
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

**Location:** [terraform/user_data.sh](../terraform/user_data.sh) lines 17-23

---

### 3. Docker Buildx Version Too Old

**Issue:** AL2023 includes buildx 0.12.1, but docker-compose requires 0.17 or later.

**Symptom:**
```
compose build requires buildx 0.17 or later
```

**Root Cause:** Amazon Linux 2023 package repository has outdated buildx version.

**Fix Applied:** Added buildx installation to `terraform/user_data.sh`:
```bash
# Install Docker Buildx (required for docker-compose build)
echo "Installing Docker Buildx..."
mkdir -p /root/.docker/cli-plugins
curl -L "https://github.com/docker/buildx/releases/download/v0.17.1/buildx-v0.17.1.linux-amd64" -o /root/.docker/cli-plugins/docker-buildx
chmod +x /root/.docker/cli-plugins/docker-buildx
```

**Location:** [terraform/user_data.sh](../terraform/user_data.sh) lines 38-42

---

### 4. Missing Prerequisites (unzip)

**Issue:** AWS CLI installation fails because unzip is not installed.

**Symptom:**
```
unzip: command not found
```

**Root Cause:** AL2023 minimal image doesn't include common utilities.

**Fix Applied:** Install prerequisites early in `terraform/user_data.sh`:
```bash
# Install prerequisites (needed for later steps)
echo "Installing prerequisites..."
yum install -y unzip jq wget curl
```

**Location:** [terraform/user_data.sh](../terraform/user_data.sh) lines 13-15

---

### 5. SSM Agent Cannot Connect Without VPC Endpoints

**Issue:** EC2 in public subnet cannot connect to SSM service without VPC endpoints or NAT Gateway.

**Symptom:**
```
aws ssm describe-instance-information returns empty InstanceInformationList
```

**Root Cause:** SSM agent needs to reach AWS SSM endpoints, which requires either:
- NAT Gateway (expensive)
- VPC Endpoints (cheaper)
- Public IP with internet gateway (security risk)

**Fix Applied:** Created VPC endpoints in `terraform/vpc_endpoints.tf`:
- `com.amazonaws.${region}.ssm`
- `com.amazonaws.${region}.ssmmessages`
- `com.amazonaws.${region}.ec2messages`

**Location:** [terraform/vpc_endpoints.tf](../terraform/vpc_endpoints.tf)

---

### 6. CloudWatch Dashboard Invalid Metrics Format

**Issue:** CloudWatch metrics array format incorrect, causing validation errors.

**Symptom:**
```
The dashboard body is invalid - metrics arrays "Should NOT have more than 2 items"
```

**Root Cause:** Incorrect HCL syntax for CloudWatch metrics - using objects instead of arrays.

**Fix Applied:** Changed metrics format from object to array:
```hcl
# Before (wrong)
["AWS/EC2", "CPUUtilization", { stat = "Average", label = "EC2 CPU" }]

# After (correct)
["AWS/EC2", "CPUUtilization", "InstanceId", aws_instance.app.id]
```

**Location:** [terraform/cloudwatch.tf](../terraform/cloudwatch.tf) lines 236-262

---

### 7. Missing IAM Policy Resource

**Issue:** `aws_iam_policy.secrets_read` was referenced but not defined.

**Symptom:**
```
Terraform error: Reference to undeclared resource
```

**Fix Applied:** Added complete IAM policy resource for Secrets Manager read access.

**Location:** [terraform/ec2.tf](../terraform/ec2.tf) lines 29-52

---

### 8. Route53 Records Already Exist

**Issue:** Terraform attempting to create A records that already exist from previous deployments.

**Symptom:**
```
Tried to create resource record set but it already exists
```

**Fix Applied:** Manual deletion via AWS CLI:
```bash
aws route53 change-resource-record-sets --hosted-zone-id Z00320409BFWAM57MKQD \
  --change-batch '{"Changes":[{"Action":"DELETE",...}]}'
```

**Recommendation:** Use `terraform import` or `terraform state rm` for cleaner handling.

---

### 9. Wrong .env File Name

**Issue:** docker-compose.prod.yml expects `.env.production` but we created `.env.prod`

**Symptom:**
```
env file /opt/credentialmate/.env.production not found
```

**Fix Applied:** Renamed file on EC2:
```bash
mv .env.prod .env.production
```

**Recommendation:** Standardize on `.env.production` naming convention throughout project.

---

### 10. Missing POSTGRES_PASSWORD Variable

**Issue:** docker-compose.prod.yml requires POSTGRES_PASSWORD even when using RDS.

**Symptom:** Docker compose warning about missing variable.

**Fix Applied:** Added `POSTGRES_PASSWORD=notused` to .env.production

**Recommendation:** Remove local postgres container from prod compose if using RDS exclusively, or make the variable optional.

---

### 11. DATABASE_URL Password Mismatch

**Issue:** .env.production had old/incorrect database password.

**Symptom:**
```
FATAL: password authentication failed for user "credentialmate"
```

**Root Cause:** The .env.prod file had an old password that didn't match the current RDS master password in terraform.tfvars.

**Fix Applied:** Updated DATABASE_URL in .env.production with correct password:
```
DATABASE_URL=postgresql://credentialmate:EpYaiJvMCWEsuFBoSsbAW29zi6a+20TJ@credentialmate-production-db.cm1ksgqm0c00.us-east-1.rds.amazonaws.com:5432/credentialmate?sslmode=require
```

---

### 12. RDS Requires SSL Connection

**Issue:** RDS PostgreSQL rejects connections without SSL encryption.

**Symptom:**
```
FATAL: no pg_hba.conf entry for host "10.0.1.67", user "credentialmate", database "credentialmate", no encryption
```

**Root Cause:** AWS RDS enforces SSL by default for security.

**Fix Applied:** Added `?sslmode=require` to DATABASE_URL:
```
postgresql://...?sslmode=require
```

---

### 13. Docker Compose depends_on_disabled Error

**Issue:** Broken docker-compose.prod.yml after failed sed command.

**Symptom:**
```
depends_on_disabled not allowed
```

**Root Cause:** A sed command to modify the file corrupted the YAML syntax.

**Fix Applied:** Restored file from git:
```bash
git checkout -- docker-compose.prod.yml
```

---

### 14. Container Environment Variables Not Updated After .env Change

**Issue:** After updating .env.production, backend container still had old DATABASE_URL.

**Symptom:** Database connection failures persisted after fixing .env file.

**Root Cause:** Docker containers read environment variables at startup time. A `restart` doesn't reload the .env file.

**Fix Applied:** Force recreate the container:
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --force-recreate backend
```

---

### 15. Database Migrations Not Run

**Issue:** Users table doesn't exist, causing 500 errors on registration.

**Symptom:**
```
500 Internal Server Error on POST /api/auth/register
```

**Root Cause:** Alembic migrations were never executed against the RDS database.

**Fix Required:** Run migrations after container is healthy:
```bash
docker exec credentialmate-backend alembic upgrade head
```

**Status:** Pending - migrations need to be run to complete deployment.

---

## Deployment Checklist for Future Builds

### Pre-Deployment
- [ ] Ensure terraform.tfvars exists with all required secrets
- [ ] Verify EC2 key pair exists in AWS
- [ ] Check Route53 hosted zone exists
- [ ] Confirm domain DNS is configured
- [ ] Verify .env.production has matching DATABASE_URL password

### Terraform Apply
- [ ] Run `terraform init`
- [ ] Run `terraform plan -out=tfplan`
- [ ] Review plan carefully
- [ ] Run `terraform apply tfplan`
- [ ] Wait for RDS to become available (~10-15 min)

### EC2 Setup
- [ ] Wait for cloud-init to complete: `cloud-init status --wait`
- [ ] Verify SSM agent is online: `aws ssm describe-instance-information`
- [ ] Confirm swap is enabled: `free -m` (should show ~2GB swap)
- [ ] Verify Docker buildx version: `docker buildx version` (should be 0.17+)

### SSL Certificate
- [ ] Stop any process using port 80
- [ ] Run certbot: `certbot certonly --standalone -d credentialmate.com -d www.credentialmate.com`
- [ ] Verify certs exist: `ls /etc/letsencrypt/live/credentialmate.com/`
- [ ] Copy certs to nginx/ssl directory if needed

### Application Deployment
- [ ] Clone repository to /opt/credentialmate
- [ ] Create .env.production with all required variables (use correct DB password!)
- [ ] Run docker-compose: `docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --build`
- [ ] Monitor build progress (expect 5-8 minutes on t3.micro)
- [ ] Verify all containers are healthy: `docker ps`

### Database Setup
- [ ] Run migrations: `docker exec credentialmate-backend alembic upgrade head`
- [ ] Seed initial data if needed: `docker exec credentialmate-backend python -m app.scripts.seed_all_data`

### Verification
- [ ] Test HTTPS: `curl -sk https://credentialmate.com`
- [ ] Test health endpoint: `curl -sk https://credentialmate.com/health`
- [ ] Test registration flow in browser
- [ ] Test login flow

---

## Cost Breakdown

| Resource | Monthly Cost | Notes |
|----------|-------------|-------|
| EC2 t3.micro | ~$7.66 | Consider t3.small for faster builds |
| RDS db.t4g.micro | ~$11.05 | Minimum viable database |
| EBS 20GB gp3 | ~$1.60 | Adequate for Docker images |
| VPC Endpoints (3x) | ~$21.90 | Required for SSM without NAT |
| Elastic IP | ~$3.65 | Free when attached to running instance |
| Route53 Hosted Zone | ~$0.50 | Per hosted zone per month |
| **Total** | **~$46/month** | Without NAT Gateway |

---

## Security Improvements Implemented

1. **IAM Roles Instead of Credentials** - EC2 uses IAM instance profile for AWS service access
2. **Encrypted EBS** - Root volume is encrypted at rest
3. **IMDSv2 Required** - Enhanced instance metadata security (prevents SSRF attacks)
4. **SSL/TLS Encryption** - Let's Encrypt certificates for HTTPS
5. **RDS SSL** - Database connections require encryption
6. **Security Groups** - Minimal port exposure (22, 80, 443 only)
7. **VPC Endpoints** - Private connectivity to AWS services

---

## Files Modified During This Deployment

1. `terraform/ec2.tf` - Added block_device_mappings for 20GB volume, IAM policies
2. `terraform/user_data.sh` - Added prerequisites, swap, buildx installation
3. `terraform/vpc_endpoints.tf` - New file for SSM VPC endpoints
4. `terraform/cloudwatch.tf` - Fixed dashboard metrics format
5. `docs/DEPLOYMENT-GAPS-AND-FIXES.md` - Deployment documentation

---

## Remaining Tasks

### Immediate
- [ ] Run database migrations on EC2
- [ ] Verify user registration works
- [ ] Test complete user flow (register, login, upload document)

### Short-term
- [ ] Set up automated certificate renewal cron job
- [ ] Configure CloudWatch alarms with SNS email notifications
- [ ] Enable RDS automated backups
- [ ] Add health check monitoring

### Long-term
- [ ] Set up CI/CD pipeline for automated deployments
- [ ] Consider upgrading to t3.small for faster builds
- [ ] Implement blue-green deployment strategy
- [ ] Add application performance monitoring (APM)

---

## Lessons Learned

1. **Always verify environment variable sources** - The .env file password mismatch cost significant debugging time
2. **Force recreate containers after env changes** - `restart` doesn't reload environment variables
3. **Test SSM connectivity early** - VPC endpoints are essential for SSM without NAT Gateway
4. **AL2023 is minimal** - Many utilities (unzip, jq) need explicit installation
5. **t3.micro needs swap** - 1GB RAM is insufficient for Docker builds
6. **Check buildx version** - docker-compose requires buildx 0.17+
7. **Plan for disk space** - Docker images need more than 2GB default volume
8. **RDS requires SSL** - Always include `?sslmode=require` in DATABASE_URL

---

## Useful Commands Reference

### EC2 Instance Management
```bash
# Get instance ID
aws ec2 describe-instances --filters "Name=tag:Name,Values=credentialmate-production-app-server" --query "Reservations[0].Instances[0].InstanceId" --output text

# Check SSM connectivity
aws ssm describe-instance-information

# Run command via SSM
aws ssm send-command --instance-ids <instance-id> --document-name "AWS-RunShellScript" --parameters "commands=[\"<command>\"]"

# Taint EC2 for rebuild
terraform taint aws_instance.app
```

### Docker Management
```bash
# Check container status
docker ps

# View logs
docker logs credentialmate-backend --tail 100

# Run migrations
docker exec credentialmate-backend alembic upgrade head

# Force recreate with new env
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --force-recreate backend
```

### SSL Certificate
```bash
# Obtain certificate
certbot certonly --standalone -d credentialmate.com -d www.credentialmate.com

# Verify certificate
openssl s_client -connect credentialmate.com:443 -servername credentialmate.com
```

---

## Current Deployment Status

**Date:** November 20, 2025
**Status:** Nearly Complete - Pending Database Migrations

**Working:**
- Infrastructure deployed (VPC, EC2, RDS, S3)
- SSL certificate obtained and configured
- All 5 Docker containers running (nginx, frontend, backend, postgres, redis)
- Health endpoint responding: https://credentialmate.com/health

**Pending:**
- Database migrations need to be executed
- User registration verification after migrations

---

*Document created: November 20, 2025*
*Instance ID: i-07ac286e2cd25c26f*
*EC2 IP: Check terraform output for current Elastic IP*
