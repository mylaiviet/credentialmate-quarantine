# ============================================
# Terraform Outputs
# CredentialMate - Infrastructure Information
# ============================================

# Network Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

# Compute Outputs
output "ec2_instance_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.app.public_dns
}

output "application_url" {
  description = "Application URL"
  value       = "https://${var.domain_name}"
}

# Database Outputs
output "rds_instance_id" {
  description = "ID of the RDS instance"
  value       = aws_db_instance.main.id
}

output "rds_database_name" {
  description = "Name of the database"
  value       = var.db_name
}

# Storage Outputs
output "s3_bucket_region" {
  description = "Region of the S3 bucket"
  value       = aws_s3_bucket.documents.region
}

# Monitoring Outputs
output "monitoring_dashboard" {
  description = "CloudWatch dashboard for monitoring"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

# Security Outputs
output "kms_key_ids" {
  description = "KMS key IDs for encryption"
  value = {
    rds = aws_kms_key.rds.id
    s3  = aws_kms_key.s3.id
  }
  sensitive = true
}

# DNS Outputs
output "nameservers_instructions" {
  description = "Instructions for DNS setup"
  value       = var.create_route53_zone ? "Update your domain registrar with these nameservers: ${join(", ", aws_route53_zone.main[0].name_servers)}" : "Using existing Route53 hosted zone"
}

# Deployment Information
output "deployment_info" {
  description = "Deployment information and next steps"
  value = <<-EOT
    ============================================
    CredentialMate Infrastructure Deployed!
    ============================================

    Application URL: https://${var.domain_name}
    Load Balancer: ${aws_lb.main.dns_name}
    EC2 Instance: ${aws_instance.app.id}
    RDS Endpoint: ${aws_db_instance.main.endpoint}

    Next Steps:
    1. Configure DNS (if needed):
       ${var.create_route53_zone ? "Update nameservers at your domain registrar" : "Verify DNS records"}

    2. Verify SSL certificate:
       - Check ACM console for validation status
       - DNS validation records created automatically

    3. Deploy application:
       - SSH to EC2: ssh -i <key>.pem ec2-user@${aws_eip.app.public_ip}
       - Run deployment: /opt/credentialmate/deploy.sh --seed

    4. Monitor application:
       - Dashboard: ${aws_cloudwatch_dashboard.main.dashboard_name}
       - Logs: /aws/${var.project_name}/${var.environment}/application

    5. Access Secrets Manager:
       - Database: ${var.project_name}/${var.environment}/database
       - App Secrets: ${var.project_name}/${var.environment}/app

    Cost Estimate:
    - EC2 t3.micro: ~$7.66/month
    - RDS t4g.micro: ~$11.05/month
    - NAT Gateway: ~$32/month (optional, can disable)
    - Total: ~$20-50/month for 10 users

    ============================================
  EOT
}
