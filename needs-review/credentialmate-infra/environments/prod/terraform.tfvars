# ============================================
# Production Environment Configuration
# ============================================

environment = "prod"
aws_region  = "us-east-1"

# VPC Configuration (Multiple AZs for HA)
vpc_cidr           = "10.0.0.0/16"
enable_nat_gateway = true
enable_vpn         = true

# Database Configuration
db_engine                = "postgres"
db_version               = "15"
db_instance_class        = "db.t3.large" # Larger instance for prod
db_allocated_storage     = 100           # More storage for prod
flow_logs_retention_days = 90            # Longer retention for compliance

# Logging
log_retention_days = 90 # 90 days minimum for SOC2/HIPAA

# ACM Certificate ARN (Must be manually created)
acm_certificate_arn = "arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERT_ID"

# SNS Topics for Alerts
sns_topic_arns = [
  "arn:aws:sns:us-east-1:ACCOUNT_ID:security-alerts"
]

# Tags
tags = {
  Application = "CredentialMate"
  Compliance  = "SOC2-HIPAA"
  Environment = "prod"
  CostCenter  = "Engineering"
}
