# ============================================
# Terraform Providers Configuration
# CredentialMate - AWS Infrastructure
# ============================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  # Backend configuration for state management
  # Uncomment after creating the S3 bucket manually
  # backend "s3" {
  #   bucket         = "credentialmate-terraform-state"
  #   key            = "production/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "credentialmate-terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "CredentialMate"
      Environment = var.environment
      ManagedBy   = "Terraform"
      HIPAA       = "true"
      CostCenter  = "Infrastructure"
    }
  }
}
