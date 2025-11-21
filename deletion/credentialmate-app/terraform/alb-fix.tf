# ============================================
# ALB Configuration FIX
# CredentialMate - Corrected Nginx Target Group
# ============================================
#
# ISSUE: Original config pointed to backend:8000 instead of nginx:80
# FIX: Updated target group to use port 80 and correct health check path
#
# To apply this fix:
# 1. Rename this file to replace alb.tf OR
# 2. Copy the nginx target group section to alb.tf
# 3. Run: terraform plan && terraform apply
# ============================================

# Target Group for Nginx (Reverse Proxy Entry Point)
resource "aws_lb_target_group" "nginx" {
  name     = "credentialmate-prod-nginx"
  port     = 80  # ✅ Nginx listens on port 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2  # ✅ Faster failure detection
    timeout             = 5
    interval            = 15  # ✅ Faster health checks (was 30)
    path                = "/health"  # ✅ Nginx forwards to backend
    protocol            = "HTTP"
    matcher             = "200"
    port                = "traffic-port"  # ✅ Use same port as target
  }

  deregistration_delay = 30

  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400
    enabled         = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-nginx-tg"
  }
}

# Register EC2 instance with nginx target group (port 80)
resource "aws_lb_target_group_attachment" "nginx" {
  target_group_arn = aws_lb_target_group.nginx.arn
  target_id        = aws_instance.app.id
  port             = 80  # ✅ EC2 instance nginx port
}

# HTTPS Listener (primary) - forwards to nginx
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.main.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.nginx.arn  # ✅ Forward to nginx
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-https-listener"
  }
}

# HTTP Listener (redirect to HTTPS)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-http-listener"
  }
}

# Optional: Keep backend target group for direct backend access (debugging)
# This is NOT used by ALB, only for manual testing
resource "aws_lb_target_group" "backend_debug" {
  name     = "credentialmate-prod-backend-debug"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"  # ✅ Backend /health endpoint
    protocol            = "HTTP"
    matcher             = "200"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-backend-debug-tg"
  }
}

# Outputs
output "nginx_target_group_arn" {
  description = "ARN of the nginx target group"
  value       = aws_lb_target_group.nginx.arn
}

output "nginx_target_group_name" {
  description = "Name of the nginx target group"
  value       = aws_lb_target_group.nginx.name
}
