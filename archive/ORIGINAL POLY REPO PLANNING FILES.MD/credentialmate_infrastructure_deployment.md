# **CredentialMate Infrastructure & Deployment Document**
## **Version 1.0 — Canonical AWS Architecture, CI/CD, Environment Parity, Rollbacks & DR**
### **Sources Incorporated:**
- Section 27 — Deployment Strategy
- Section 20 — Security Monitoring
- Section 16 — Tech Stack & TCO
- ECS vs EC2 guidance
- Terraform multi-environment structure
- Disaster Recovery (DR) plan
- Rollback strategy
- Data Bible v2.0
- SAD v1.0

---
# **1. PURPOSE OF THIS DOCUMENT**
This Infrastructure & Deployment Document defines the **canonical AWS deployment architecture** for CredentialMate, including:
- ECS + RDS + VPC architecture
- Terraform infrastructure-as-code structure
- CI/CD pipelines
- Failover & Disaster Recovery
- Zero-downtime deployments
- Security boundary enforcement
- Multi-environment parity (dev, stage, prod)
- Rollback strategies
- Cost optimization (TCO)

This document is authoritative for DevOps, infra agents, backend engineers, security teams, and auditors.

---
# **2. CANONICAL AWS ARCHITECTURE**
CredentialMate uses a **HIPAA-grade**, **zero-trust**, **NAT-optional**, **VPC-endpoint-first** architecture.

## **2.1 Core Components**
- **VPC (3-tier)**
- **ECS Fargate services**
- **RDS PostgreSQL 15**
- **S3 (documents)**
- **ALB (HTTPS ingress only)**
- **Secrets Manager**
- **CloudWatch logs + metrics**
- **VPC Endpoints** for S3, SES, CloudWatch, Secrets Manager
- **ECR** for container registry

---
# **3. VPC ARCHITECTURE**
```
VPC
├── Public Subnets
│   └── ALB (HTTPS only)
├── Private Subnets A/B
│   ├── ECS Tasks (frontend + backend)
│   └── RDS PostgreSQL (encrypted)
└── VPC Endpoints
    ├── com.amazonaws.s3
    ├── com.amazonaws.ses
    ├── com.amazonaws.secretsmanager
    └── com.amazonaws.logs
```
### **Why NAT Is Optional**
Because infrastructure uses:
- VPC endpoints
- No external API dependencies
- ECS pulls images from ECR

NAT can be added **later** if you introduce external vendors.

---
# **4. ECS FARGATE ARCHITECTURE**
## **4.1 Services**
- `frontend-service` (Next.js)
- `backend-service` (FastAPI)
- `parser-service` (future worker)
- `notification-worker` (future worker)

## **4.2 Runtime Characteristics**
- Stateless containers
- Read-only root filesystem
- Secrets injected via IAM task roles
- Horizontal autoscaling
- Blue/green or rolling updates via ECS

---
# **5. RDS POSTGRESQL ARCHITECTURE**
## **5.1 Configuration**
- Multi-AZ optional
- KMS encryption
- Automated backups (7–30 days)
- Backup window: off-peak
- Parameter group: logging enabled
- Performance Insights enabled

## **5.2 Access Controls**
- RDS accessible ONLY from ECS task SG
- No public access EVER
- IAM authentication optional

## **5.3 Migration Strategy**
- Alembic migrations generated in dev
- Approved manually in prod
- Applied via CI/CD with human gate

---
# **6. S3 DOCUMENT ARCHITECTURE**
- Versioning required
- SSE-S3 or SSE-KMS encryption
- ACLs disabled (bucket owner enforced)
- Pre-signed URLs for access
- Lifecycle rules optional (no deletion of raw PHI)

---
# **7. TERRAFORM INFRASTRUCTURE-AS-CODE**
## **7.1 Repo Structure**
```
/terraform
   /modules
      /vpc
      /ecs-service
      /ecs-cluster
      /rds
      /s3
      /alb
      /security-groups
      /iam
   /environments
      /dev
      /stage
      /prod
```

## **7.2 Module Requirements**
- No hardcoded values
- Use variables + outputs
- Enforce tagging standards (CostCenter, App, Owner, Env)
- Provider version pinned

## **7.3 Environment Parity Rules**
- Same architecture between dev/stage/prod
- Different sizing only
- Same Terraform modules
- Same security boundaries
- Same IAM design

---
# **8. CI/CD ARCHITECTURE**
## **8.1 GitHub Actions Structure**
```
Build → Test → Security Scan → Push to ECR → Deploy to ECS
```

## **8.2 Pipelines**
### **Backend Pipeline**
- pytest
- mypy
- flake8
- docker build
- push to ECR
- update ECS service

### **Frontend Pipeline**
- npm install
- build
- dockerize
- push to ECR
- ECS deploy

### **Terraform Pipeline**
- fmt
- validate
- plan (manual approval)
- apply (admin-only)

## **8.3 Security Scanning**
- Trivy container scans
- Bandit for Python
- npm audit / yarn audit
- IaC scan (tfsec or Checkov)

## **8.4 Human Approval Gates**
Required for:
- migrations
- production deploys
- Terraform applies

---
# **9. ROLLBACK STRATEGY**
## **9.1 ECS Application Rollback**
- Deploys create a new task revision
- ECS → rollback to previous revision in 1 click
- Blue/green with automatic rollback if healthchecks fail

## **9.2 Database Rollback**
- Use reversible Alembic migrations only
- Never deploy destructive migrations without backups
- Point-in-time restore available

## **9.3 S3 Rollback**
- Use versioning: restore earlier object

---
# **10. DISASTER RECOVERY (DR) PLAN**
## **10.1 RDS Multi-AZ**
Failover in <60 seconds.

## **10.2 Backup & Restore**
- PITR (point-in-time recovery)
- Snapshot restore to new instance
- S3 snapshots export optional

## **10.3 ECS Task Recovery**
- Health checks auto-restart unhealthy tasks
- Minimum healthy percent = 100%

## **10.4 S3 Durability**
- 11 nines (99.999999999%)
- Multi-AZ by default

## **10.5 DR Environment (Optional Future)**
- Separate AWS region
- Terraform workspace: `/dr`
- Cross-region S3 replication

---
# **11. SECURITY ARCHITECTURE (FROM SECTION 20)**
## **11.1 IAM Model**
- ECS task roles (least privilege)
- Developer roles separate from admin
- No long-lived access keys
- Mandatory MFA

## **11.2 Network Security**
- Security group whitelisting
- No inbound traffic to private subnets
- No public RDS

## **11.3 Secrets**
- Secrets Manager for all sensitive values
- Auto-rotation optional

## **11.4 Logging & Monitoring**
- CloudWatch logs
- RDS performance metrics
- ECS task logs
- Audit logs from backend

---
# **12. OBSERVABILITY (INTEGRATED)**
## **12.1 Metrics**
- API latency
- Parsing job duration
- Notification success rate
- Compliance engine execution time

## **12.2 Alerts**
- ECS task crash
- ALB 5xx surge
- RDS CPU > 70%
- Low free storage
- SES bounce rate escalation

---
# **13. COST OPTIMIZATION (TCO)**
## **13.1 ECS Fargate Savings**
- Run minimal vCPU/memory
- Autoscale only when needed

## **13.2 NAT Removal Option**
- Save ~$32/mo + data transfer
- Use VPC endpoints exclusively

## **13.3 RDS Tiering**
- Start with t4g.micro or t4g.small
- Scale only when >100 users/day

## **13.4 CloudWatch Log Retention**
- 30–90 days depending on needs

---
# **14. FORBIDDEN INFRASTRUCTURE ACTIONS**
Infra agents and developers may NEVER:
- Deploy unreviewed Terraform to prod
- Open public access to RDS
- Disable S3 encryption
- Push secrets to GitHub
- Destroy prod resources without backup
- Modify IAM roles without approval

---
# **15. FUTURE EXPANSIONS**
- Multi-region failover
- KMS key rotation policies
- Global accelerator
- PrivateLink integrations with vendors
- Container sidecars for compliance scanning

---
# **SUMMARY OF WHAT WAS ADDED AT YOUR REQUEST**
Below is the list of **missing or expanded elements** I added:

### 🔥 **1. Full Terraform module & environment structure**
Clearly defined folders, modules, parity rules.

### 🔥 **2. Rollback strategy (ECS + RDS + S3)**
Complete guidance for app + data + document rollback.

### 🔥 **3. Disaster Recovery Plan (DR)**
Multi-AZ, PITR, cross-region replication.

### 🔥 **4. Security architecture (IAM, secrets, monitoring)**
From Section 20 + SAD.

### 🔥 **5. Observability integration**
Metrics, logs, alerts tied to ECS/RDS/SES.

### 🔥 **6. Cost optimization (TCO)**
How to reduce cost with ECS + endpoints + RDS tiering.

### 🔥 **7. Explicit removal of NAT (optional)**
Explained architecture and reasons.

### 🔥 **8. Forbidden infrastructure actions**
To enforce compliance and safety.

### 🔥 **9. Infrastructure

