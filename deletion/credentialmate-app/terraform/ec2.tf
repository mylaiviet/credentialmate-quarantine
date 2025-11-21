# ============================================
# EC2 Configuration
# CredentialMate - Application Server
# ============================================

# IAM Role for EC2 Instance
resource "aws_iam_role" "ec2_app" {
  name = "${var.project_name}-${var.environment}-ec2-app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-ec2-app-role"
  }
}

# Attach Secrets Manager read policy
resource "aws_iam_role_policy_attachment" "ec2_secrets" {
  role       = aws_iam_role.ec2_app.name
  policy_arn = aws_iam_policy.secrets_read.arn
}

# Attach SSM policy for Systems Manager access
resource "aws_iam_role_policy_attachment" "ec2_ssm" {
  role       = aws_iam_role.ec2_app.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# S3 Access Policy for EC2
resource "aws_iam_policy" "s3_documents_access" {
  name        = "${var.project_name}-${var.environment}-s3-documents-access"
  description = "Allow EC2 to access S3 documents bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:PutObjectAcl"
        ]
        Resource = [
          aws_s3_bucket.documents.arn,
          "${aws_s3_bucket.documents.arn}/*"
        ]
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-s3-documents-access-policy"
  }
}

resource "aws_iam_role_policy_attachment" "ec2_s3" {
  role       = aws_iam_role.ec2_app.name
  policy_arn = aws_iam_policy.s3_documents_access.arn
}

# Bedrock Access Policy for EC2
resource "aws_iam_policy" "bedrock_access" {
  name        = "${var.project_name}-${var.environment}-bedrock-access"
  description = "Allow EC2 to invoke Bedrock models"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
        ]
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-bedrock-access-policy"
  }
}

resource "aws_iam_role_policy_attachment" "ec2_bedrock" {
  role       = aws_iam_role.ec2_app.name
  policy_arn = aws_iam_policy.bedrock_access.arn
}

# CloudWatch Logs Policy for EC2
resource "aws_iam_policy" "cloudwatch_logs" {
  name        = "${var.project_name}-${var.environment}-cloudwatch-logs"
  description = "Allow EC2 to write to CloudWatch Logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:log-group:/aws/${var.project_name}/*"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-cloudwatch-logs-policy"
  }
}

resource "aws_iam_role_policy_attachment" "ec2_cloudwatch" {
  role       = aws_iam_role.ec2_app.name
  policy_arn = aws_iam_policy.cloudwatch_logs.arn
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "ec2_app" {
  name = "${var.project_name}-${var.environment}-ec2-app-profile"
  role = aws_iam_role.ec2_app.name

  tags = {
    Name = "${var.project_name}-${var.environment}-ec2-app-profile"
  }
}

# Latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# User data script for EC2 initialization
data "template_file" "user_data" {
  template = file("${path.module}/user_data.sh")

  vars = {
    project_name = var.project_name
    environment  = var.environment
    aws_region   = var.aws_region
  }
}

# EC2 Launch Template
resource "aws_launch_template" "app" {
  name_prefix   = "${var.project_name}-${var.environment}-"
  image_id      = data.aws_ami.amazon_linux_2023.id
  instance_type = var.ec2_instance_type
  key_name      = var.ec2_key_name != "" ? var.ec2_key_name : null

  iam_instance_profile {
    name = aws_iam_instance_profile.ec2_app.name
  }

  vpc_security_group_ids = [aws_security_group.ec2_app.id]

  user_data = base64encode(data.template_file.user_data.rendered)

  monitoring {
    enabled = var.enable_detailed_monitoring
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.project_name}-${var.environment}-app-server"
    }
  }

  tag_specifications {
    resource_type = "volume"
    tags = {
      Name = "${var.project_name}-${var.environment}-app-volume"
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-launch-template"
  }
}

# EC2 Instance
resource "aws_instance" "app" {
  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  subnet_id = aws_subnet.public[0].id

  tags = {
    Name        = "${var.project_name}-${var.environment}-app-server"
    Backup      = "Required"
    Monitoring  = "Enabled"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Elastic IP for EC2 (optional, for static IP)
resource "aws_eip" "app" {
  instance = aws_instance.app.id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-app-eip"
  }

  depends_on = [aws_internet_gateway.main]
}

# Outputs
output "ec2_instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.app.id
}

output "ec2_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_eip.app.public_ip
}

output "ec2_private_ip" {
  description = "Private IP of the EC2 instance"
  value       = aws_instance.app.private_ip
}
