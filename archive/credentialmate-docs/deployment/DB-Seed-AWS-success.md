# DB-Seed-AWS Success

## Overview
This document describes the process of seeding test data into the AWS production database for CredentialMate, the barriers encountered, and solutions implemented.

## Date
2025-11-20

## Instance Details
- **EC2 Instance ID**: `i-07ac286e2cd25c26f`
- **Application Directory**: `/opt/credentialmate`
- **Backend Container**: `credentialmate-backend`

---

## Task Summary
Create seed data in AWS production with custom credentials:
- Email pattern: `provmd1@test.com`, `provmd2@test.com`, etc.
- Password for ALL users: `Test1234`
- Do NOT modify any existing code files

---

## Process Steps

### 1. Find Seed Scripts
Used the Explore agent to search for existing seed scripts in the codebase.

**Key files found:**
- `credentialmate-app/backend/app/scripts/seed_all_data.py` - Master orchestration script
- `credentialmate-app/backend/app/scripts/seed_users_admins.py` - User seeding
- Other phase-specific seed scripts for credentials, CME activities, etc.

### 2. Identify AWS Remote Execution Method
Found SSM (AWS Systems Manager) is used for remote command execution:
- `get_ssm_output.py` - Helper to retrieve SSM command output
- `deploy_migrations.py` - Example of SSM deployment pattern

### 3. Check EC2 Environment
```bash
aws ssm describe-instance-information --query "InstanceInformationList[*].[InstanceId,PingStatus]"
```
Confirmed instance `i-07ac286e2cd25c26f` was online.

### 4. Locate Application Directory
Initial attempt to use `/home/ec2-user/credentialmate-app` failed.
Discovered actual location: `/opt/credentialmate`

### 5. Run Database Migrations
Database tables didn't exist - got error: `relation "users" does not exist`

**Solution:**
```bash
aws ssm send-command --instance-ids i-07ac286e2cd25c26f \
  --document-name "AWS-RunShellScript" \
  --parameters '{"commands":["cd /opt/credentialmate && docker exec credentialmate-backend alembic upgrade head"]}'
```

### 6. Create Custom Seed Script
Created `seed_custom_production.py` locally with:
- Custom email patterns (`provmd1@test.com`, etc.)
- Unified password `Test1234`
- Users, notification settings, and delegations

### 7. Transfer Script to EC2
Used base64 encoding to transfer the Python script via SSM.

### 8. Execute Seed Script
```bash
docker cp /tmp/seed_custom.py credentialmate-backend:/tmp/seed_custom.py
docker exec credentialmate-backend python /tmp/seed_custom.py
```

---

## Barriers Encountered and Solutions

### Barrier 1: SSM Command String Escaping
**Problem**: Long base64 strings and special characters caused shell parsing errors:
```
unexpected EOF while looking for matching `"'
```

**Solution**: Use a JSON file for SSM parameters instead of inline JSON:
```bash
# Create ssm_seed_command.json with the command
aws ssm send-command --instance-ids i-07ac286e2cd25c26f \
  --document-name "AWS-RunShellScript" \
  --parameters file://c:/CM-MULTI-REPO/ssm_seed_command.json
```

### Barrier 2: Character Encoding Issues (Windows)
**Problem**: SSM output contains Unicode characters that Windows cp1252 encoding can't display:
```
'charmap' codec can't encode characters in position 0-1: character maps to <undefined>
```

**Solution**:
- Check `Status` separately (always works)
- Filter output through grep to remove problematic characters:
```bash
docker exec ... python -c '...' 2>/dev/null | grep -E '@test.com'
```

### Barrier 3: Database Tables Not Existing
**Problem**: Attempting to query users before running migrations:
```
psycopg2.errors.UndefinedTable: relation "users" does not exist
```

**Solution**: Run Alembic migrations first:
```bash
docker exec credentialmate-backend alembic upgrade head
```

### Barrier 4: Wrong Application Directory
**Problem**: Initially assumed `/home/ec2-user/credentialmate-app` but got:
```
cd: /home/ec2-user/credentialmate-app: No such file or directory
```

**Solution**: Search for the actual directory:
```bash
find /home /opt -name 'credentialmate-app' -type d
ls -la /opt/
```
Discovered it's at `/opt/credentialmate`

### Barrier 5: AWS Secrets Manager Warnings
**Problem**: Container shows warning about credentials:
```
BotoCore error retrieving secret credentialmate/prod/database: Unable to locate credentials
```

**Solution**: This is a non-fatal warning. The application falls back to environment variables. Ignore unless critical functionality fails.

---

## Verification Commands

### Check User Count
```bash
aws ssm send-command --instance-ids i-07ac286e2cd25c26f \
  --document-name "AWS-RunShellScript" \
  --parameters '{"commands":["docker exec credentialmate-backend python -c \"from app.core.database import SessionLocal; from app.models.user import User; db = SessionLocal(); print(db.query(User).count()); db.close()\" 2>/dev/null | grep -E \"^[0-9]+$\""]}'
```

### List All User Emails
```bash
aws ssm send-command --instance-ids i-07ac286e2cd25c26f \
  --document-name "AWS-RunShellScript" \
  --parameters '{"commands":["docker exec credentialmate-backend python -c \"from app.core.database import SessionLocal; from app.models.user import User; db = SessionLocal(); [print(u.email) for u in db.query(User).all()]; db.close()\" 2>/dev/null | grep -E \"@test.com\""]}'
```

---

## Final Results

### Users Created (32 total)

| Role | Count | Email Pattern | Password |
|------|-------|---------------|----------|
| Admin | 3 | `admin@test.com`, `compliance@test.com`, `support@test.com` | Test1234 |
| Delegate | 4 | `delegate1@test.com` - `delegate4@test.com` | Test1234 |
| MD Provider | 18 | `provmd1@test.com` - `provmd18@test.com` | Test1234 |
| DO Provider | 7 | `provdo1@test.com` - `provdo7@test.com` | Test1234 |

### Additional Data
- 32 Notification settings
- 75 Admin delegations (3 admins × 25 providers)
- 12 Delegate delegations

---

## Key Learnings for Future Agents

1. **Always check application directory first** - Don't assume standard paths like `/home/ec2-user`

2. **Use JSON files for complex SSM commands** - Avoids shell escaping nightmares:
   ```bash
   --parameters file://path/to/command.json
   ```

3. **Run migrations before seeding** - Database tables must exist first

4. **Filter SSM output for Windows compatibility** - Use `grep` to remove Unicode characters

5. **Check Status separately from Output** - Status check always works even when output has encoding issues

6. **Use `2>/dev/null` to suppress warnings** - Cleaner output, easier parsing

7. **Base64 encode large scripts** - Transfer via:
   ```bash
   echo '<base64>' | base64 -d > /tmp/script.py
   docker cp /tmp/script.py container:/tmp/
   docker exec container python /tmp/script.py
   ```

8. **Docker container name**: `credentialmate-backend` (not just `backend`)

---

## Files Created During This Process

- `c:\CM-MULTI-REPO\seed_custom_production.py` - The custom seed script
- `c:\CM-MULTI-REPO\ssm_seed_command.json` - SSM command parameters file

---

## Quick Reference Commands

### Get SSM Instance Status
```bash
aws ssm describe-instance-information --query "InstanceInformationList[*].[InstanceId,PingStatus,AgentVersion]" --output table
```

### Send SSM Command
```bash
aws ssm send-command --instance-ids i-07ac286e2cd25c26f \
  --document-name "AWS-RunShellScript" \
  --parameters '{"commands":["your command here"]}' \
  --query "Command.CommandId" --output text
```

### Get SSM Command Result
```bash
aws ssm get-command-invocation --command-id <COMMAND_ID> \
  --instance-id i-07ac286e2cd25c26f \
  --query "[Status, StandardOutputContent]" --output text
```

### Execute in Docker Container
```bash
docker exec credentialmate-backend <command>
docker exec credentialmate-backend python -c '<python code>'
docker exec credentialmate-backend alembic upgrade head
```
