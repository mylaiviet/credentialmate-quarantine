# TIMESTAMP: 2025-11-20T20:39:15Z
# CLASSIFICATION: SOC2 Type II - User Documentation
# COMPLIANCE: HIPAA, SOC2
# ORIGIN: credentialmate-app
# PURPOSE: Repository documentation and quick start guide

# CredentialMate - Terraform Infrastructure

HIPAA-compliant AWS infrastructure for CredentialMate production deployment.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Route 53 DNS                          │
│                   credentialmate.com                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            Application Load Balancer (ALB)                   │
│          SSL/TLS Termination (ACM Certificate)               │
│              HTTPS (443) → HTTP (8000)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┴───────────────┐
       │                               │
       ▼                               ▼
┌──────────────┐              ┌──────────────┐
│ Public Subnet│              │Public Subnet │
│   (us-east-1a)│              │  (us-east-1b)│
│              │              │              │
│  ┌────────┐  │              │              │
│  │  EC2   │  │              │              │
│  │ t3.micro│  │              │              │
│  │(Docker)│  │              │              │
│  └────────┘  │              │              │
└──────┬───────┘              └──────────────┘
       │
       │ Private Network
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│               Private Subnets (Database Tier)                │
│                                                              │
│  ┌──────────────┐                   ┌──────────────┐        │
│  │    RDS       │                   │   RDS        │        │
│  │  PostgreSQL  │◄─────────────────►│  (Standby)   │        │
│  │  t4g.micro   │   Multi-AZ (opt)  │              │        │
│  │  Encrypted   │                   │              │        │
│  └──────────────┘                   └──────────────┘        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      AWS Services                            │
│                                                              │
│  S3 (Encrypted)  │  Secrets Manager  │  CloudWatch          │
│  ├─ Documents    │  ├─ DB Creds      │  ├─ Logs             │
│  └─ Access Logs  │  └─ App Secrets   │  ├─ Metrics          │
│                  │                   │  └─ Alarms           │
└─────────────────────────────────────────────────────────────┘
```

## Cost Breakdown

### Minimal Configuration (10 users)
```
EC2 t3.micro:          $7.66/month
RDS t4g.micro:         $11.05/month
Route 53:              $1.50/month
S3 Storage:            $0.33/month
NAT Gateway:           $32.00/month (optional)
────────────────────────────────────
Total (no NAT):        $20.54/month
Total (with NAT):      $52.54/month
```

### Production Configuration (100 users)
```
EC2 t3.small:          $15.33/month
RDS t4g.small:         $29.20/month
Route 53:              $1.50/month
S3 Storage:            $3.30/month
NAT Gateway:           $32.00/month
────────────────────────────────────
Total:                 $81.33/month
```

## Prerequisites

- AWS CLI v2+
- Terraform v1.5+
- AWS account with AdministratorAccess
- Domain name (credentialmate.com)

## Quick Start

### 1. Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:
```hcl
domain_name    = "credentialmate.com"
db_password    = "YOUR_SECURE_PASSWORD"
app_secret_key = "YOUR_SECRET_KEY"
jwt_secret_key = "YOUR_JWT_SECRET"
encryption_key = "YOUR_ENCRYPTION_KEY"
alarm_email    = "admin@credentialmate.com"
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Review Plan

```bash
terraform plan
```

### 4. Deploy

```bash
terraform apply
```

## Module Structure

```
terraform/
├── providers.tf           # AWS provider & backend configuration
├── variables.tf           # Input variables
├── terraform.tfvars       # Variable values (DO NOT COMMIT!)
├── terraform.tfvars.example  # Example values
│
├── vpc.tf                 # VPC, subnets, networking
├── security_groups.tf     # Security groups (ALB, EC2, RDS)
├── ec2.tf                 # EC2 instance & IAM roles
├── rds.tf                 # PostgreSQL database
├── s3.tf                  # S3 buckets for documents
├── secrets_manager.tf     # AWS Secrets Manager
├── alb.tf                 # Application Load Balancer
├── route53.tf             # DNS records
├── cloudwatch.tf          # Monitoring & alarms
├── outputs.tf             # Output values
│
├── user_data.sh           # EC2 initialization script
└── README.md              # This file
```

## Resources Created

### Network (vpc.tf)
- VPC (10.0.0.0/16)
- Public subnets (2 AZs)
- Private subnets (2 AZs)
- Internet Gateway
- NAT Gateway (optional)
- Route tables
- VPC Flow Logs

### Compute (ec2.tf)
- EC2 instance (t3.micro)
- IAM role with policies:
  - Secrets Manager read
  - S3 documents access
  - Bedrock invoke
  - CloudWatch Logs
  - SSM (Systems Manager)
- Elastic IP
- User data script (Docker setup)

### Database (rds.tf)
- PostgreSQL 15.5
- Instance: db.t4g.micro (ARM)
- Storage: 20GB GP3, autoscaling to 100GB
- Encrypted with KMS
- Automated backups (35 days)
- Multi-AZ: disabled (enable for HA)
- Enhanced monitoring
- Performance Insights

### Storage (s3.tf)
- Documents bucket (encrypted, versioned)
- Access logs bucket
- Lifecycle policies (Glacier after 90 days)
- Block public access
- CORS configuration

### Security (secrets_manager.tf)
- Database credentials secret
- Application secrets secret
- AWS credentials secret
- KMS encryption keys (RDS, S3)

### Load Balancer (alb.tf)
- Application Load Balancer
- SSL/TLS certificate (ACM)
- HTTPS listener (443)
- HTTP → HTTPS redirect (80)
- Target groups (backend:8000, streamlit:8501)
- Health checks

### DNS (route53.tf)
- A records (root, www)
- Certificate validation records
- Health check
- CloudWatch alarm for health

### Monitoring (cloudwatch.tf)
- Log groups (application, Docker)
- Alarms:
  - EC2 CPU > 80%
  - RDS CPU > 80%
  - RDS storage < 2GB
  - ALB 5xx errors > 10
  - Failed logins > 10
  - Unhealthy targets
- SNS topic for alerts
- CloudWatch dashboard

## Security Features

### HIPAA Compliance
- ✅ Encryption at rest (RDS, S3, EBS)
- ✅ Encryption in transit (SSL/TLS, RDS force SSL)
- ✅ Automated backups (35 days)
- ✅ Audit logging (VPC Flow Logs, CloudWatch)
- ✅ Access controls (IAM, Security Groups)
- ✅ KMS key rotation
- ✅ No public database access

### Network Security
- Private subnets for database
- Security groups (least privilege)
- VPC Flow Logs
- NAT Gateway for outbound traffic

### Application Security
- SSL/TLS termination at ALB
- Security headers middleware
- httpOnly cookies
- CORS restrictions
- Rate limiting

## Configuration Options

### Cost Optimization

Disable NAT Gateway to save $32/month:
```hcl
enable_nat_gateway = false
```

**Impact**: Private subnets can't reach internet (RDS can't download updates, EC2 can't pull from ECR from private subnet).

### High Availability

Enable multi-AZ RDS:
```hcl
# In rds.tf
multi_az = true
```

**Cost**: Doubles RDS cost (~$22/month instead of ~$11/month).

### Scaling

Upgrade instance types:
```hcl
ec2_instance_type = "t3.small"   # $15.33/month
db_instance_class = "db.t4g.small"  # $29.20/month
```

## Outputs

After deployment, get outputs:

```bash
terraform output
```

Key outputs:
- `application_url`: https://credentialmate.com
- `ec2_public_ip`: EC2 instance IP for SSH
- `rds_endpoint`: Database connection string
- `s3_documents_bucket_name`: S3 bucket for uploads
- `cloudwatch_dashboard_url`: Monitoring dashboard

## Maintenance

### Update Infrastructure

```bash
# Pull latest Terraform config
git pull

# Review changes
terraform plan

# Apply updates
terraform apply
```

### Backup & Restore

**Database**:
```bash
# Manual snapshot
aws rds create-db-snapshot \
    --db-instance-identifier credentialmate-production-db \
    --db-snapshot-identifier manual-$(date +%Y%m%d)

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier credentialmate-restored \
    --db-snapshot-identifier manual-20250118
```

**Terraform State**:
```bash
# Download current state
terraform state pull > terraform.tfstate.backup

# Restore state (if needed)
terraform state push terraform.tfstate.backup
```

### Destroy Infrastructure

**WARNING**: This will delete ALL resources!

```bash
# Disable deletion protection first
# In rds.tf, set: deletion_protection = false
terraform apply

# Destroy
terraform destroy
```

## Troubleshooting

### Common Issues

1. **SSL certificate not validating**
   - Check Route 53 records exist
   - Wait 5-30 minutes for DNS propagation
   - Verify domain nameservers

2. **RDS connection failed**
   - Check security group allows EC2 → RDS
   - Verify Secrets Manager has correct credentials
   - Check RDS is in "available" state

3. **Terraform state locked**
   ```bash
   # Force unlock (use with caution!)
   terraform force-unlock LOCK_ID
   ```

4. **High costs**
   - Check NAT Gateway ($32/month)
   - Review CloudWatch billable metrics
   - Check S3 storage class transitions

### Debug Commands

```bash
# View current state
terraform show

# List all resources
terraform state list

# Inspect specific resource
terraform state show aws_instance.app

# Refresh state
terraform refresh

# Validate configuration
terraform validate
```

## Best Practices

1. **Never commit**:
   - `terraform.tfvars`
   - `*.tfstate`
   - `*.tfstate.backup`
   - `.terraform/`

2. **Always use state locking** (DynamoDB)

3. **Use workspaces for environments**:
   ```bash
   terraform workspace new staging
   terraform workspace select production
   ```

4. **Tag all resources** for cost tracking

5. **Enable deletion protection** on critical resources

6. **Use Terraform Cloud** for team collaboration (optional)

## Support

- **Documentation**: [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md)
- **AWS Console**: https://console.aws.amazon.com/
- **Terraform Docs**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs

---

**Infrastructure as Code for HIPAA-Compliant Healthcare SaaS** 🏥
