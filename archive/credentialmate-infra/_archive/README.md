# Archive Directory

This directory contains deprecated configurations archived for historical reference.
These files are NOT used in production and should NOT be modified.

## Archived Items

### terraform-legacy/
**Archived:** 2025-11-20
**Reason:** Superseded by modular Terraform approach in `modules/` and `environments/`
**Reference:** Original monolithic Terraform implementation from initial development

### legacy/
**Archived:** 2025-11-20
**Reason:** AI Build Orchestrator configuration no longer used
**Reference:** Historical orchestration setup from early development phases

### scripts/deploy-to-production.sh
**Archived:** 2025-11-20
**Reason:** Functionality duplicated by `scripts/deploy-ec2-production.sh`
**Note:** Contains inline docker-compose generation; canonical compose is now `deployment/docker-compose.prod.yml`

## Usage Warning

**Do not use these files for deployment or reference in CI/CD pipelines.**

For current configurations, use:
- **Docker Compose:** `deployment/docker-compose.prod.yml`
- **Nginx Config:** `deployment/nginx.conf`
- **Terraform:** `environments/{dev,staging,prod}/`
- **Deployment Script:** `scripts/deploy-ec2-production.sh`
