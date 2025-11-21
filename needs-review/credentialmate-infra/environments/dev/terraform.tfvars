# ============================================
# Development Environment Configuration
# ============================================

environment = "dev"
aws_region  = "us-east-1"

# VPC Configuration
vpc_cidr           = "10.2.0.0/16"
enable_nat_gateway = true
enable_vpn         = false # VPN not needed for dev

# Database Configuration
db_engine                = "postgres"
db_version               = "15"
db_instance_class        = "db.t3.micro" # Minimal instance for dev
db_allocated_storage     = 20            # Minimal storage for dev
flow_logs_retention_days = 7

# Logging
log_retention_days = 7 # 7 days for dev (minimal)

# ACM Certificate ARN
acm_certificate_arn = "arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/DEV_CERT_ID"

# SNS Topics (optional for dev)
sns_topic_arns = []

# Tags
tags = {
  Application = "CredentialMate"
  Compliance  = "SOC2-HIPAA"
  Environment = "dev"
  CostCenter  = "Engineering"
}
