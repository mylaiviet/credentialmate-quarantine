# Terraform Migration Manifest

## Overview
This document describes the migration from the monolithic terraform configuration in `credentialmate-app/terraform/` to the modularized infrastructure in `credentialmate-infra/`.

## Source Folder Structure (credentialmate-app/terraform/)

```
terraform/
├── alb.tf                 # Application Load Balancer configuration
├── alb-fix.tf             # ALB fixes/patches
├── cloudwatch.tf          # CloudWatch monitoring, logs, alarms
├── ec2.tf                 # EC2 instance configuration
├── outputs.tf             # Terraform outputs
├── providers.tf           # AWS provider configuration
├── rds.tf                 # RDS PostgreSQL database
├── README.md              # Documentation
├── route53.tf             # DNS configuration
├── s3.tf                  # S3 buckets for documents
├── security_groups.tf     # Security group rules
├── terraform.tfstate      # Current state file (LOCAL)
├── terraform.tfvars       # Variable values (contains secrets)
├── terraform.tfvars.example # Example variables
├── tfplan                 # Last terraform plan
├── user_data.sh           # EC2 user data script
├── variables.tf           # Variable definitions
└── vpc.tf                 # VPC, subnets, routing
```

## Target Infrastructure Module Structure (credentialmate-infra/)

```
credentialmate-infra/
├── main.tf                    # Root module composition
├── variables.tf               # Root variables
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
└── modules/
    ├── alb/                   # Application Load Balancer
    ├── dynamodb/              # DynamoDB tables
    ├── ecs/                   # ECS (future container deployment)
    ├── lambda/                # Lambda functions
    ├── lambda_stuck_job_detection/
    ├── monitoring/            # CloudWatch dashboards & alarms
    ├── rds/                   # RDS PostgreSQL
    ├── s3/                    # S3 buckets
    ├── sns/                   # SNS notifications
    └── vpc/                   # VPC networking
```

## Per-File Migration Mapping

| Source File (app/terraform) | Target Module (infra) | Notes |
|----------------------------|----------------------|-------|
| `alb.tf` | `modules/alb/` | Migrate to ALB module |
| `alb-fix.tf` | `modules/alb/` | Merge fixes into main ALB module |
| `cloudwatch.tf` | `modules/monitoring/` | Split into dashboard + alarms |
| `ec2.tf` | Root or new `modules/ec2/` | Consider ECS migration path |
| `rds.tf` | `modules/rds/` | Migrate to RDS module |
| `route53.tf` | Root or new `modules/dns/` | DNS configuration |
| `s3.tf` | `modules/s3/` | Migrate to S3 module |
| `security_groups.tf` | `modules/vpc/` or dedicated | Part of VPC or standalone |
| `vpc.tf` | `modules/vpc/` | Migrate to VPC module |
| `providers.tf` | Root `main.tf` | Provider in root module |
| `variables.tf` | Module `variables.tf` | Split per module |
| `outputs.tf` | Module `outputs.tf` | Split per module |
| `user_data.sh` | `modules/ec2/` or templates | EC2 bootstrap script |

## State Migration Requirements

### Current State
- **Location**: `credentialmate-app/terraform/terraform.tfstate` (LOCAL file)
- **Backend**: Local filesystem (no remote state)
- **Hash**: See `state-hash.txt` for SHA256 verification

### Migration Steps

1. **Backup State**
   ```bash
   cp terraform.tfstate terraform.tfstate.backup
   ```

2. **Configure Remote Backend** (recommended)
   ```hcl
   terraform {
     backend "s3" {
       bucket         = "credentialmate-terraform-state"
       key            = "prod/terraform.tfstate"
       region         = "us-east-1"
       encrypt        = true
       dynamodb_table = "terraform-locks"
     }
   }
   ```

3. **State Move Operations**
   For each resource being moved to a module:
   ```bash
   terraform state mv aws_lb.main module.alb.aws_lb.main
   terraform state mv aws_db_instance.main module.rds.aws_db_instance.main
   terraform state mv aws_vpc.main module.vpc.aws_vpc.main
   # ... continue for all resources
   ```

4. **Import Existing Resources** (if recreating)
   ```bash
   terraform import module.alb.aws_lb.main <alb-arn>
   terraform import module.rds.aws_db_instance.main <db-identifier>
   ```

### Critical Warnings

- **DO NOT** delete or modify `terraform.tfstate` until migration is complete
- **DO NOT** run `terraform destroy` on old configuration
- **ALWAYS** run `terraform plan` after state moves to verify no-change expectation
- State locking via DynamoDB is recommended for team use

## No-Change Apply Expectation

After successful migration, running `terraform plan` should show:

```
No changes. Your infrastructure matches the configuration.
```

### Verification Checklist

- [ ] All resources appear in `terraform state list`
- [ ] `terraform plan` shows 0 to add, 0 to change, 0 to destroy
- [ ] `terraform apply` completes with no changes
- [ ] Resource attributes match AWS console
- [ ] Outputs produce expected values

### Troubleshooting

If plan shows changes:
1. Compare resource attributes between old and new configs
2. Check for default value differences
3. Verify provider version compatibility
4. Use `terraform state show <resource>` to inspect state

## Resources to Migrate

Based on source files, approximately these resource types need migration:

- VPC, Subnets, Route Tables, Internet Gateway, NAT Gateway
- Security Groups
- Application Load Balancer, Target Groups, Listeners
- RDS PostgreSQL instance
- S3 Buckets (documents, backups)
- CloudWatch Log Groups, Metric Alarms, Dashboard
- Route53 Records
- EC2 Instance(s)
- IAM Roles and Policies

## Timeline Considerations

Migration should be performed during a maintenance window with:
- Database backups completed
- Application scaled down or in maintenance mode
- DNS TTLs reduced prior to migration
- Rollback plan documented

---

**Generated**: 2024-11-20
**Archive Location**: `credentialmate-quarantine/archive/terraform-app-legacy/`
