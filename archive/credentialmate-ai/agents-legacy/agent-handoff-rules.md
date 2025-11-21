<!-- SOC2 Control: AI-AGT-002 | HIPAA: §164.312(a)(1) -->
<!-- Owner: Agent Team -->
<!-- Classification: Internal -->
<!-- Last Review: 2025-11-20 -->

# AI Agent Handoff Rules

## 🔄 Error Handling: 3-Strike Rule

When you encounter an error, you get **3 attempts** to fix it:

### Attempt 1: Direct Fix (Confidence >90%)
**Duration**: 5-10 minutes

1. Read the error message carefully
2. Check .orchestration/ISSUES_LOG.md for similar errors
3. Apply direct fix if confident
4. Test fix
5. If fixed: ✅ Update .orchestration/CHANGES_LOG.md and .orchestration/ISSUES_LOG.md
6. If not fixed: → Go to Attempt 2

### Attempt 2: Research & Alternative Approach
**Duration**: 10-15 minutes

1. Research the error (web search, documentation)
2. Try a different approach
3. Check if issue is environmental
4. Test alternative fix
5. If fixed: ✅ Document in .orchestration/ISSUES_LOG.md with research notes
6. If not fixed: → Go to Attempt 3

### Attempt 3: Deep Dive (Last Chance)
**Duration**: 15-20 minutes

1. Investigate root cause thoroughly
2. Check related systems (database, network, dependencies)
3. Try most comprehensive fix
4. Add extensive logging
5. Test with different scenarios
6. If fixed: ✅ Document thoroughly (this was hard)
7. If not fixed: → Escalate

### Escalation Process

**After 3 failed attempts:**

1. **Document what you tried**:
   ```
   Issue: [Error message]
   Attempt 1: [What you tried] → [Result]
   Attempt 2: [What you tried] → [Result]
   Attempt 3: [What you tried] → [Result]
   Current state: [Broken/Partially working/Unknown]
   ```

2. **Determine escalation path**:

   **If: Another AI agent might know**
   - Ask Cursor AI if frontend-related
   - Ask Claude Code if backend-related
   - Ask Codex if scripting-related

   **If: Human intervention needed**
   - Create GitHub issue
   - Tag user for help
   - Document in .orchestration/ISSUES_LOG.md as "Needs Review"
   - Continue with other tasks (don't block)

3. **What NOT to do**:
   - ❌ Try same fix 10 times hoping it works
   - ❌ Make random changes
   - ❌ Break working code to fix unrelated issue
   - ❌ Give up without documenting what was tried

## 🤝 Agent-to-Agent Communication

### When to Loop in Another Agent

**Cursor AI → Claude Code**:
- "Backend API returning unexpected data format"
- "Need clarification on API contract"
- "Database query needed for frontend feature"

**Claude Code → Cursor AI**:
- "Frontend not consuming API correctly"
- "Need UI component to display backend data"
- "Breaking API change, need frontend update"

**Any Agent → ChatGPT Codex**:
- "Need test data for this feature"
- "Need script to migrate data"
- "Need utility function for data processing"

### Communication Format

```markdown
## Agent Handoff Request

**From**: [Your agent name]
**To**: [Target agent name]
**Priority**: [High/Medium/Low]
**Context**: [Brief description of situation]

**What I need**:
[Specific request]

**What I've tried**:
- [Attempt 1]
- [Attempt 2]
- [Attempt 3]

**Related files**:
- path/to/file.py
- path/to/another.tsx

**Deadline**: [If time-sensitive]
```

### Where to Leave Handoff Messages

1. **GitHub Issues**: For formal requests
2. **Pull Request Comments**: For code review requests
3. **.orchestration/CHANGES_LOG.md**: For coordination notices
4. **Module README**: For integration notes

## 🔗 Integration Handoff Protocol

### Before Integration

**Backend (Claude Code) → Frontend (Cursor AI)**:

1. [ ] Complete backend feature
2. [ ] Write API-CONTRACT.md documentation
3. [ ] Create sample requests/responses
4. [ ] Write integration tests
5. [ ] Update CONTRACT-VERSIONS.yaml
6. [ ] Notify Cursor AI via PR comment

**Frontend (Cursor AI) → Backend (Claude Code)**:

1. [ ] Document frontend requirements
2. [ ] Specify expected API endpoints
3. [ ] Provide UI mockups (if needed)
4. [ ] Define data structures needed
5. [ ] Update MODULE-README.md
6. [ ] Notify Claude Code via GitHub issue

### During Integration

1. **Test together**: Both agents verify integration works
2. **Document issues**: Use .orchestration/ISSUES_LOG.md for any problems
3. **Update contracts**: Reflect actual implementation
4. **Run sync-check**: Ensure no version drift

### After Integration

1. **Integration tests**: Must pass before merge
2. **Update documentation**: Both agents verify accuracy
3. **Close related issues**: Link PR to issues
4. **Notify team**: Update .orchestration/CHANGES_LOG.md

## 📋 Handoff Checklist

### When Completing Your Work

**Before marking module as "complete":**

1. [ ] All tests passing
2. [ ] Documentation updated
3. [ ] .orchestration/CHANGES_LOG.md updated
4. [ ] API-CONTRACT.md current (if applicable)
5. [ ] No known issues (or documented in .orchestration/ISSUES_LOG.md)
6. [ ] Integration points tested
7. [ ] Other agents notified (if they depend on this)
8. [ ] Pull request created
9. [ ] Code review requested (if needed)
10. [ ] CI/CD pipeline passing

### When Receiving Handoff

**Before starting work on handed-off module:**

1. [ ] Read handoff documentation
2. [ ] Review API-CONTRACT.md
3. [ ] Check .orchestration/CHANGES_LOG.md for recent updates
4. [ ] Verify environment setup
5. [ ] Run existing tests to confirm baseline
6. [ ] Ask questions if anything unclear
7. [ ] Acknowledge receipt of handoff

## 🚦 Handoff Status Indicators

### In MODULE-README.md

```markdown
## Module Status

**Owner**: [Agent name]
**Status**: [In Progress / Ready for Review / Ready for Integration / Complete]
**Last Updated**: YYYY-MM-DD HH:MM CST
**Depends On**: [List of other modules]
**Blocks**: [List of modules waiting on this]

### Handoff Status
- [ ] Backend complete
- [ ] Frontend complete
- [ ] Integration tested
- [ ] Documentation complete
- [ ] Ready for production
```

## 🎯 Quick Reference

### I need help with...

**Backend issues** → Ask Claude Code
**Frontend issues** → Ask Cursor AI
**Script/data issues** → Ask ChatGPT Codex
**Architecture decisions** → Ask User
**Security concerns** → Ask User
**HIPAA compliance** → Ask User

### When to escalate...

**After 3 failed attempts** → Escalate to another agent or user
**Security-related changes** → Escalate to user immediately
**Breaking changes** → Coordinate with affected agents
**Protected resources** → Ask user for permission
**Unclear requirements** → Ask user for clarification

---

**Remember**: Communication prevents duplication, reduces errors, and builds better software. When in doubt, ask.
