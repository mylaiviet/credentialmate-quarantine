# CredentialMate Terraform Outputs
# Session: 20251109-174043

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "Public subnet ID"
  value       = aws_subnet.public.id
}

output "private_subnet_id" {
  description = "Private subnet ID"
  value       = aws_subnet.private.id
}

output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.postgres.endpoint
  sensitive   = true
}

output "rds_address" {
  description = "RDS database address (without port)"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "RDS database port"
  value       = aws_db_instance.postgres.port
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.postgres.db_name
}

output "s3_documents_bucket" {
  description = "S3 documents bucket name"
  value       = aws_s3_bucket.documents.id
}

output "s3_backups_bucket" {
  description = "S3 backups bucket name"
  value       = aws_s3_bucket.backups.id
}

output "elastic_ip" {
  description = "Elastic IP for EC2 instance"
  value       = aws_eip.ec2.public_ip
}

output "ec2_security_group_id" {
  description = "EC2 security group ID"
  value       = aws_security_group.ec2.id
}

output "ec2_instance_profile" {
  description = "EC2 IAM instance profile name"
  value       = aws_iam_instance_profile.ec2.name
}

output "db_password_secret_arn" {
  description = "ARN of DB password in Secrets Manager"
  value       = aws_secretsmanager_secret.db_password.arn
  sensitive   = true
}

output "jwt_secret_arn" {
  description = "ARN of JWT secret in Secrets Manager"
  value       = aws_secretsmanager_secret.jwt_secret.arn
  sensitive   = true
}

output "route53_nameservers" {
  description = "Route 53 nameservers (update your domain registrar)"
  value = [
    "ns-1549.awsdns-01.co.uk",
    "ns-1230.awsdns-25.org",
    "ns-640.awsdns-16.net",
    "ns-234.awsdns-29.com"
  ]
}

output "ssl_certificate_arn" {
  description = "SSL certificate ARN"
  value       = var.ssl_certificate_arn
}

output "deployment_summary" {
  description = "Deployment summary and next steps"
  value       = <<-EOT

  CredentialMate Infrastructure Deployed Successfully!

  VPC CIDR: 10.1.0.0/16 (Separate from karematch)
  Region: ${var.aws_region}

  Next Steps:
  1. Update domain nameservers at your registrar
  2. Wait for SSL certificate validation (~30 minutes)
  3. Create EC2 key pair: aws ec2 create-key-pair --key-name credentialmate-key
  4. Launch EC2 instance with user data script
  5. Configure Nginx with Let's Encrypt
  6. Deploy application containers

  Database Connection:
  - Host: ${aws_db_instance.postgres.address}
  - Port: ${aws_db_instance.postgres.port}
  - Database: ${aws_db_instance.postgres.db_name}
  - Username: ${var.db_username}
  - Password: Stored in Secrets Manager

  Public IP: ${aws_eip.ec2.public_ip}

  EOT
}
