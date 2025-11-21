<!-- SOC2 Control: AI-AGT-002 | HIPAA: §164.312(a)(1) -->
<!-- Owner: Agent Team -->
<!-- Classification: Internal -->
<!-- Last Review: 2025-11-20 -->

# Code Safety Rules - MANDATORY FOR ALL AGENTS

## 🔴 CRITICAL: Investigation Protocol

**Before touching ANY code, you MUST:**

1. [ ] Read relevant documentation (max 10 minutes)
   - Check README.md for context
   - Check MODULE-README.md if working in a module
   - Check API-CONTRACT.md for integration points

2. [ ] Understand the data flow
   - Trace the request/response path
   - Identify all affected components
   - Check database queries and relationships

3. [ ] Search existing codebase
   - grep for similar patterns
   - Check if solution already exists elsewhere
   - Look for related functions/classes

4. [ ] Check .orchestration/ISSUES_LOG.md
   - Search for similar error patterns
   - Reference existing solutions if found
   - Avoid solving same problem twice

5. [ ] Read related code
   - Open files that will be affected
   - Understand current implementation
   - Identify potential side effects

**TIME LIMIT**: Max 10 minutes of investigation
**IF YOU SKIP THIS**: You will likely break something

## 🚨 When to STOP and Ask for Help

### Immediate Stop Conditions (Ask Human)
- ✋ Security-related changes (authentication, authorization, encryption)
- ✋ Database schema changes (breaking changes)
- ✋ Payment processing code (Stripe integration)
- ✋ Production deployment decisions
- ✋ Deleting code or files (unless clearly dead code)
- ✋ Changes to protected resources (see .orchestration/KNOWLEDGE_BASE.md)

### Ask for Second Opinion (Another AI Agent)
- 🤝 Stuck on same error for 3 attempts (3-strike rule)
- 🤝 Confidence <90% on solution
- 🤝 Multiple valid approaches exist
- 🤝 Change affects another agent's code
- 🤝 Breaking API contract (need coordination)

### Confidence Thresholds
- **>90% confident**: Proceed with implementation
- **80-90% confident**: Ask another AI agent for review
- **<80% confident**: Ask human for guidance

## 🛡️ Protected Resources

**NEVER edit these without explicit user permission:**

From .orchestration/KNOWLEDGE_BASE.md:
- `backend/app/core/security.py` - HIPAA compliance verified
- `backend/app/database.py` - Stable, production-tested
- `infrastructure/terraform/main.tf` - Production infrastructure

**If you need to edit a protected resource:**
1. STOP immediately
2. Document WHY it needs to change
3. Ask user: "This file is protected. May I proceed with edits?"
4. Wait for explicit approval

## ⚠️ If Code Was Working, Don't Break It

**Principle**: Additive > Destructive

When fixing Issue A:
1. [ ] Identify files affected by Issue A
2. [ ] Identify files that might be affected indirectly
3. [ ] Test affected functionality BEFORE your fix
4. [ ] Apply your fix
5. [ ] Test affected functionality AFTER your fix
6. [ ] Test RELATED functionality (don't break Feature B)

**Log WHY you made the change** in .orchestration/CHANGES_LOG.md:
- What was broken
- Why this fix was chosen
- What might be affected
- How to rollback if needed

## 📝 Documentation Requirements

**Every change must be documented:**

1. **.orchestration/CHANGES_LOG.md**: Log every change you make
   - What changed
   - Why it changed
   - Who made the change
   - When it changed

2. **.orchestration/ISSUES_LOG.md**: Log every issue you encounter
   - Error message
   - Root cause
   - Solution applied
   - Prevention strategy

3. **.orchestration/KNOWLEDGE_BASE.md**: Document lessons learned
   - Patterns that work
   - Patterns to avoid
   - Critical information

## 🔄 Integration Protocol

**When your work depends on another agent:**

1. Check API-CONTRACT.md for the module
2. Verify contract version matches your expectations
3. Test integration locally
4. Document integration in MODULE-README.md
5. Create integration tests

**When another agent depends on your work:**

1. Update API-CONTRACT.md with any changes
2. Increment version if breaking change
3. Notify other agents via PR comments
4. Provide migration guide if needed
5. Don't merge until integration tests pass

## 🚀 Testing Requirements

**Before committing code:**

1. [ ] Unit tests pass
2. [ ] Integration tests pass (if applicable)
3. [ ] Manual testing completed
4. [ ] No regressions in related features
5. [ ] Documentation updated

**If tests fail:**
- Follow 3-strike error handling protocol
- Document attempts in .orchestration/ISSUES_LOG.md
- Ask for help after 3 attempts

## 🔒 Security Checklist

**Before committing code with security implications:**

1. [ ] No hardcoded secrets or credentials
2. [ ] Input validation in place
3. [ ] SQL injection prevention (parameterized queries)
4. [ ] XSS prevention (sanitized outputs)
5. [ ] CSRF protection (if applicable)
6. [ ] Authentication required (if applicable)
7. [ ] Authorization checked (if applicable)
8. [ ] Audit logging added (if PHI involved)
9. [ ] HIPAA compliance verified
10. [ ] Security review requested

## 📊 Quality Standards

**Code must meet these standards:**

1. **Readability**:
   - Clear variable names
   - Descriptive function names
   - Comments for complex logic
   - Consistent formatting

2. **Maintainability**:
   - DRY (Don't Repeat Yourself)
   - Single Responsibility Principle
   - Small, focused functions
   - Easy to test

3. **Performance**:
   - No N+1 queries
   - Efficient algorithms
   - Proper indexing (database)
   - Caching where appropriate

4. **Error Handling**:
   - Try/catch blocks
   - Meaningful error messages
   - Logging for debugging
   - Graceful degradation

## 🎯 Summary: The 10 Commandments

1. **Investigate before coding** (max 10 minutes)
2. **Ask for help when <90% confident**
3. **Follow 3-strike rule** (escalate after 3 attempts)
4. **Never break working code**
5. **Document every change** (.orchestration/CHANGES_LOG.md)
6. **Document every issue** (.orchestration/ISSUES_LOG.md)
7. **Test before committing**
8. **Verify security** (HIPAA compliance)
9. **Coordinate with other agents** (API contracts)
10. **Don't touch protected resources** (without approval)

---

**Remember**: These rules exist to prevent issues learned from the old CME Tracker project. Following them will save time and prevent bugs.

See [docs/planning/01-LESSONS-LEARNED.md](../../docs/planning/01-LESSONS-LEARNED.md) for detailed lessons from the previous project.
