# ============================================
# RDS PostgreSQL Configuration
# CredentialMate - HIPAA-Compliant Database
# ============================================

# DB Subnet Group (required for multi-AZ deployment)
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  }
}

# DB Parameter Group (custom PostgreSQL settings)
resource "aws_db_parameter_group" "main" {
  name   = "${var.project_name}-${var.environment}-pg15-params"
  family = "postgres15"

  # HIPAA Compliance: Enable SSL
  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }

  # Audit logging (HIPAA requirement)
  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  parameter {
    name  = "log_duration"
    value = "1"
  }

  # Performance optimizations for t4g.micro
  parameter {
    name  = "shared_buffers"
    value = "{DBInstanceClassMemory/32768}"
  }

  parameter {
    name  = "effective_cache_size"
    value = "{DBInstanceClassMemory/16384}"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-pg15-params"
  }
}

# KMS Key for RDS Encryption (HIPAA requirement)
resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-kms-key"
  }
}

resource "aws_kms_alias" "rds" {
  name          = "alias/${var.project_name}-${var.environment}-rds"
  target_key_id = aws_kms_key.rds.key_id
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}-db"

  # Engine Configuration
  engine               = "postgres"
  engine_version       = "15.15"
  instance_class       = var.db_instance_class
  parameter_group_name = aws_db_parameter_group.main.name

  # Storage Configuration
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  # Database Configuration
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  # Network Configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  multi_az               = false # Set to true for production HA (doubles cost)

  # Backup Configuration (HIPAA requires 35+ days)
  backup_retention_period   = var.db_backup_retention_period
  backup_window             = "03:00-04:00"
  maintenance_window        = "Mon:04:00-Mon:05:00"
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  # Deletion Protection (HIPAA/SOC2 requirement)
  deletion_protection       = true
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.project_name}-${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  copy_tags_to_snapshot     = true

  # Monitoring
  performance_insights_enabled    = true
  performance_insights_retention_period = 7 # Days (free tier)
  monitoring_interval = 60 # Enhanced monitoring (free tier: 60 seconds)
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn

  # Auto minor version updates
  auto_minor_version_upgrade = true

  tags = {
    Name        = "${var.project_name}-${var.environment}-db"
    Backup      = "Required"
    Encryption  = "AES-256"
    Compliance  = "HIPAA"
  }

  lifecycle {
    # Prevent accidental deletion
    prevent_destroy = false # Set to true after initial creation
    # Ignore password changes (use AWS Secrets Manager rotation)
    ignore_changes = [password]
  }
}

# IAM Role for Enhanced Monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "${var.project_name}-${var.environment}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-monitoring-role"
  }
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# CloudWatch Log Groups (for RDS logs)
resource "aws_cloudwatch_log_group" "rds_postgresql" {
  name              = "/aws/rds/instance/${var.project_name}-${var.environment}-db/postgresql"
  retention_in_days = 90

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-postgresql-logs"
  }
}

resource "aws_cloudwatch_log_group" "rds_upgrade" {
  name              = "/aws/rds/instance/${var.project_name}-${var.environment}-db/upgrade"
  retention_in_days = 90

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-upgrade-logs"
  }
}

# Output connection string for Secrets Manager
output "rds_endpoint" {
  description = "RDS endpoint for database connection"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "rds_connection_string" {
  description = "PostgreSQL connection string"
  value       = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.endpoint}/${var.db_name}"
  sensitive   = true
}
