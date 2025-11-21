# CredentialMate Terraform Variables
# Session: 20251109-174043

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "credentialmate"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.1.0.0/16" # Different from karematch (10.0.0.0/16)
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "credentialmate"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "credentialmate"
}

variable "instance_type" {
  description = "EC2 instance type (Budget Plan: t3.micro)"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "AMI ID for EC2 instance (Ubuntu 22.04 LTS)"
  type        = string
  default     = "" # Will be looked up dynamically
}

variable "key_pair_name" {
  description = "EC2 key pair name for SSH access"
  type        = string
  default     = "" # You'll need to create this
}

variable "ssl_certificate_arn" {
  description = "ACM SSL certificate ARN"
  type        = string
  default     = "arn:aws:acm:us-east-1:051826703172:certificate/ba7178ef-07ab-49c1-a2ce-f5ae69e1b88c"
}
