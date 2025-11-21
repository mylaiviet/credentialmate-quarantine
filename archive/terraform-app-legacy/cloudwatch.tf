# ============================================
# CloudWatch Monitoring and Alarms Configuration
# CredentialMate - Production Monitoring (FREE TIER)
# ============================================

# SNS Topic for Alerts (optional, only if alarm_email is provided)
resource "aws_sns_topic" "alerts" {
  count = var.alarm_email != "" ? 1 : 0
  name  = "${var.project_name}-${var.environment}-alerts"

  tags = {
    Name = "${var.project_name}-${var.environment}-alerts"
  }
}

resource "aws_sns_topic_subscription" "alerts_email" {
  count     = var.alarm_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts[0].arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# ============================================
# EC2 CloudWatch Alarms
# ============================================

# EC2 High CPU Utilization
resource "aws_cloudwatch_metric_alarm" "ec2_cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-ec2-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors EC2 CPU utilization"
  treat_missing_data  = "notBreaching"

  dimensions = {
    InstanceId = aws_instance.app.id
  }

  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts[0].arn] : []
}

# EC2 Status Check Failed
resource "aws_cloudwatch_metric_alarm" "ec2_status_check" {
  alarm_name          = "${var.project_name}-${var.environment}-ec2-status-check-failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0
  alarm_description   = "This metric monitors EC2 instance status checks"
  treat_missing_data  = "notBreaching"

  dimensions = {
    InstanceId = aws_instance.app.id
  }

  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts[0].arn] : []
}

# ============================================
# RDS CloudWatch Alarms
# ============================================

# RDS High CPU Utilization
resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors RDS CPU utilization"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts[0].arn] : []
}

# RDS Low Free Storage Space
resource "aws_cloudwatch_metric_alarm" "rds_storage_low" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-storage-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 2147483648 # 2 GB in bytes
  alarm_description   = "This metric monitors RDS free storage space"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts[0].arn] : []
}

# RDS High Database Connections
resource "aws_cloudwatch_metric_alarm" "rds_connections_high" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-connections-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 50
  alarm_description   = "This metric monitors RDS database connections"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts[0].arn] : []
}

# ============================================
# ALB CloudWatch Alarms
# ============================================

# ALB 5xx Error Rate
resource "aws_cloudwatch_metric_alarm" "alb_5xx_errors" {
  alarm_name          = "${var.project_name}-${var.environment}-alb-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "This metric monitors ALB 5xx errors"
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts[0].arn] : []
}

# ALB Unhealthy Target Count
resource "aws_cloudwatch_metric_alarm" "alb_unhealthy_targets" {
  alarm_name          = "${var.project_name}-${var.environment}-alb-unhealthy-targets"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0
  alarm_description   = "This metric monitors unhealthy ALB targets"
  treat_missing_data  = "notBreaching"

  dimensions = {
    TargetGroup  = aws_lb_target_group.backend.arn_suffix
    LoadBalancer = aws_lb.main.arn_suffix
  }

  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts[0].arn] : []
}

# ============================================
# Application-Level Custom Metrics & Logs
# ============================================

# CloudWatch Log Group for Application Logs
resource "aws_cloudwatch_log_group" "application" {
  name              = "/aws/${var.project_name}/${var.environment}/application"
  retention_in_days = 90

  tags = {
    Name = "${var.project_name}-${var.environment}-application-logs"
  }
}

# CloudWatch Log Group for Docker Logs
resource "aws_cloudwatch_log_group" "docker" {
  name              = "/aws/${var.project_name}/${var.environment}/docker"
  retention_in_days = 30

  tags = {
    Name = "${var.project_name}-${var.environment}-docker-logs"
  }
}

# Metric Filter for Failed Login Attempts (HIPAA/SOC2 requirement)
resource "aws_cloudwatch_log_metric_filter" "failed_logins" {
  name           = "${var.project_name}-${var.environment}-failed-logins"
  log_group_name = aws_cloudwatch_log_group.application.name
  pattern        = "[time, request_id, level=ERROR, msg=\"Login failed*\"]"

  metric_transformation {
    name      = "FailedLoginAttempts"
    namespace = "CredentialMate/${var.environment}"
    value     = "1"
    unit      = "Count"
  }
}

# Alarm for Failed Login Attempts (potential security incident)
resource "aws_cloudwatch_metric_alarm" "failed_logins" {
  alarm_name          = "${var.project_name}-${var.environment}-failed-logins-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FailedLoginAttempts"
  namespace           = "CredentialMate/${var.environment}"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "This metric monitors failed login attempts (potential brute force)"
  treat_missing_data  = "notBreaching"

  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts[0].arn] : []
}

# Metric Filter for Application Errors
resource "aws_cloudwatch_log_metric_filter" "application_errors" {
  name           = "${var.project_name}-${var.environment}-application-errors"
  log_group_name = aws_cloudwatch_log_group.application.name
  pattern        = "[time, request_id, level=ERROR, ...]"

  metric_transformation {
    name      = "ApplicationErrors"
    namespace = "CredentialMate/${var.environment}"
    value     = "1"
    unit      = "Count"
  }
}

# Alarm for Application Errors
resource "aws_cloudwatch_metric_alarm" "application_errors" {
  alarm_name          = "${var.project_name}-${var.environment}-application-errors-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApplicationErrors"
  namespace           = "CredentialMate/${var.environment}"
  period              = 300
  statistic           = "Sum"
  threshold           = 20
  alarm_description   = "This metric monitors application errors"
  treat_missing_data  = "notBreaching"

  alarm_actions = var.alarm_email != "" ? [aws_sns_topic.alerts[0].arn] : []
}

# ============================================
# CloudWatch Dashboard
# ============================================

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-${var.environment}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/EC2", "CPUUtilization", { stat = "Average", label = "EC2 CPU", instanceId = aws_instance.app.id }],
            ["AWS/RDS", "CPUUtilization", { stat = "Average", label = "RDS CPU", DBInstanceIdentifier = aws_db_instance.main.id }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "CPU Utilization"
          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", { stat = "Sum", LoadBalancer = aws_lb.main.arn_suffix }],
            [".", "HTTPCode_Target_2XX_Count", { stat = "Sum", LoadBalancer = aws_lb.main.arn_suffix }],
            [".", "HTTPCode_Target_4XX_Count", { stat = "Sum", LoadBalancer = aws_lb.main.arn_suffix }],
            [".", "HTTPCode_Target_5XX_Count", { stat = "Sum", LoadBalancer = aws_lb.main.arn_suffix }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "ALB Request Metrics"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/RDS", "DatabaseConnections", { stat = "Average", DBInstanceIdentifier = aws_db_instance.main.id }],
            [".", "FreeStorageSpace", { stat = "Average", DBInstanceIdentifier = aws_db_instance.main.id, yAxis = "right" }]
          ]
          period = 300
          region = var.aws_region
          title  = "RDS Connections & Storage"
        }
      },
      {
        type = "log"
        properties = {
          query   = "SOURCE '${aws_cloudwatch_log_group.application.name}' | fields @timestamp, @message | filter level = 'ERROR' | sort @timestamp desc | limit 20"
          region  = var.aws_region
          title   = "Recent Application Errors"
        }
      }
    ]
  })
}

# Outputs
output "cloudwatch_dashboard_url" {
  description = "URL to CloudWatch dashboard"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "sns_topic_arn" {
  description = "ARN of SNS topic for alerts"
  value       = var.alarm_email != "" ? aws_sns_topic.alerts[0].arn : "No alarm email configured"
}
