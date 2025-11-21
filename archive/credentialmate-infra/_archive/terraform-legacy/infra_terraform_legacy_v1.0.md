# TIMESTAMP: 2025-11-20T00:00:00Z
# CLASSIFICATION: SOC2 Type II - Infrastructure Legacy Documentation
# COMPLIANCE: HIPAA technical safeguards, SOC2 infrastructure controls
# ORIGIN: credentialmate-infra
# PURPOSE: Legacy Terraform infrastructure documentation

# CredentialMate AWS Infrastructure

**Deployment Plan**: Budget ($27/month)
**Session**: 20251109-174043
**Agent**: Claude (Orchestration)

## Architecture Overview

- **VPC**: 10.1.0.0/16 (completely separate from karematch)
- **EC2**: t3.micro (2 vCPU, 1 GB RAM)
- **RDS**: db.t3.micro Single-AZ PostgreSQL 15
- **S3**: Documents + Backups buckets (encrypted)
- **SSL**: ACM certificate for credentialmate.com
- **DNS**: Route 53 hosted zone

## Prerequisites

1. ✅ AWS account with BAA signed
2. ✅ AWS CLI configured with credentials
3. ✅ Terraform installed (v1.5+)
4. ✅ Domain nameservers updated to Route 53
5. ⏳ SSL certificate validated (wait ~30 minutes)

## Quick Start

### Step 1: Create terraform.tfvars

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

### Step 2: Create EC2 Key Pair

```bash
aws ec2 create-key-pair --key-name credentialmate-key --query 'KeyMaterial' --output text > credentialmate-key.pem
chmod 400 credentialmate-key.pem  # Linux/Mac
```

### Step 3: Initialize Terraform

```bash
terraform init
```

### Step 4: Plan Infrastructure

```bash
terraform plan -out=tfplan
```

### Step 5: Apply Infrastructure

```bash
terraform apply tfplan
```

This will create:
- VPC with public/private subnets
- RDS PostgreSQL database (encrypted)
- S3 buckets (encrypted, versioned)
- Security groups
- IAM roles and policies
- Secrets Manager entries
- Elastic IP

## Important Outputs

After `terraform apply`, you'll get:

- **elastic_ip**: Public IP for your EC2 instance
- **rds_endpoint**: Database connection string
- **s3_documents_bucket**: S3 bucket for documents
- **route53_nameservers**: Nameservers to update at registrar

## Update Domain Nameservers

Update your domain registrar (wherever you registered credentialmate.com) with these nameservers:

```
ns-1549.awsdns-01.co.uk
ns-1230.awsdns-25.org
ns-640.awsdns-16.net
ns-234.awsdns-29.com
```

## Next Steps After Terraform

1. **Wait for DNS propagation** (24-48 hours)
2. **Wait for SSL validation** (~30 minutes after DNS propagation)
3. **Launch EC2 instance** (see ../ec2/launch.sh)
4. **Deploy application** (see ../ec2/deploy.sh)

## Cost Breakdown

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| EC2 | t3.micro | $7.60 |
| RDS | db.t3.micro Single-AZ | $15.25 |
| S3 | 5 GB + Glacier | $1.15 |
| Bedrock | ~500K tokens | $1.50 |
| Route 53 | 1 hosted zone | $0.50 |
| Secrets Manager | 2 secrets | $0.80 |
| Data Transfer | 5 GB | $0.45 |
| **Total** | | **$27.25/month** |

## Security Features

- ✅ VPC with private subnets
- ✅ RDS encrypted at rest (AES-256)
- ✅ S3 buckets encrypted (AES-256)
- ✅ S3 versioning enabled
- ✅ Security groups (least privilege)
- ✅ IAM roles (no hardcoded credentials)
- ✅ Secrets Manager for passwords
- ✅ Public access blocked on RDS
- ✅ Public access blocked on S3

## HIPAA Compliance

- ✅ BAA signed with AWS
- ✅ Encryption at rest (RDS, S3)
- ✅ Encryption in transit (TLS 1.2+)
- ✅ Access control (IAM, Security Groups)
- ✅ Audit logging (CloudWatch Logs)
- ✅ Automated backups (7 days)
- ✅ All services HIPAA-eligible

## Terraform State

**Important**: Terraform state contains sensitive data (passwords, etc.)

### Option 1: Local State (default)
- State stored in `terraform.tfstate`
- **DO NOT commit to git**
- Already in `.gitignore`

### Option 2: Remote State (recommended for production)
Uncomment backend configuration in `main.tf` and create S3 bucket:

```bash
aws s3 mb s3://credentialmate-terraform-state
aws dynamodb create-table --table-name credentialmate-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

## Troubleshooting

### SSL Certificate Not Validating
- Check DNS propagation: `nslookup _8bc6b6ccacac833a4c01000251c7daa7.credentialmate.com`
- Wait up to 48 hours for DNS propagation
- Verify CNAME record in Route 53

### RDS Connection Issues
- Check security group allows connection from EC2
- Verify RDS is in private subnet
- Check VPC and subnet configuration

### S3 Access Issues
- Verify IAM role attached to EC2
- Check IAM policy permissions
- Verify VPC endpoint for S3

## Destroying Infrastructure

**WARNING**: This will delete all resources including data!

```bash
terraform destroy
```

Before destroying:
1. Backup RDS database
2. Download important S3 files
3. Export any configuration

## Support

Session: 20251109-174043
Documentation: docs/planning/10-AWS-BUDGET-MIGRATION-PLAN.md
