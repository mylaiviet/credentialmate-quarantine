# ============================================
# Staging Environment Configuration
# ============================================

environment = "staging"
aws_region  = "us-east-1"

# VPC Configuration
vpc_cidr           = "10.1.0.0/16"
enable_nat_gateway = true
enable_vpn         = false # VPN not needed for staging

# Database Configuration
db_engine                = "postgres"
db_version               = "15"
db_instance_class        = "db.t3.small" # Smaller instance for staging
db_allocated_storage     = 50            # Less storage for staging
flow_logs_retention_days = 30

# Logging
log_retention_days = 30 # 30 days for staging

# ACM Certificate ARN
acm_certificate_arn = "arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/STAGING_CERT_ID"

# SNS Topics
sns_topic_arns = [
  "arn:aws:sns:us-east-1:ACCOUNT_ID:staging-alerts"
]

# Tags
tags = {
  Application = "CredentialMate"
  Compliance  = "SOC2-HIPAA"
  Environment = "staging"
  CostCenter  = "Engineering"
}
