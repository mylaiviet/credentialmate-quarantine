# ============================================================================
# CredentialMate Terraform Variables - Production
# ============================================================================
# IMPORTANT: Do NOT commit this file to version control (contains secrets)
# ============================================================================

# AWS Configuration
aws_region = "us-east-1"

# Project
project_name = "credentialmate"
environment  = "production"

# EC2 Configuration
instance_type    = "t3.small"  # 2 vCPU, 2GB RAM (~$15/month)
key_name         = "credentialmate-prod-key-2025"
allowed_ssh_cidr = "136.34.120.196/32"  # Your IP address for SSH access

# Domain Configuration
domain_name         = "credentialmate.com"
create_route53_zone = false  # Set to true if you need to create a new hosted zone
route53_zone_id     = ""     # Add your Route 53 zone ID if you have one

# Database Configuration
db_name     = "credentialmate"
db_username = "credentialmate"
db_password = "To9gYyqyZAJVYObE6EK5kFLHLF8gWCTV"

# Application Secrets
jwt_secret_key = "556a6066ca113ae1755f73915277bb0ea759052997cc14b830b9802a9d41af39"
encryption_key = "vTCV7-H4BW0hHgGT23pUt8OPUhT42YiDSk3WthoWDqw="

# Email Configuration (SES)
ses_from_email = "mylaiviet@gmail.com"

# Tags
tags = {
  Project   = "CredentialMate"
  ManagedBy = "Terraform"
  Owner     = "mylaiviet"
}