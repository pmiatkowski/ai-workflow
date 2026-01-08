---
agent: agent
description:
  Add a new work item (feature, bug, etc.). AI classifies the type automatically.
---


You are adding a new work item. Classify the type and initialize appropriately.

### 1. Extract Description

Parse the user's description from the `/ai.add` command.

If missing:

```
Please provide a description:

/ai.add {description}

Examples:
  /ai.add Fix timeout on login page
  /ai.add Allow users to reset their password
```

### 2. Classify Work Type

Analyze the description to determine if this is a **feature** or **bug**:

**Bug indicators** (fix, bug, error, broken, crash, issue, failing, timeout, etc.):

- "Fix timeout on login page" → bug
- "Login button is broken" → bug
- "Error when submitting form" → bug

**Feature indicators** (add, implement, create, allow, enable, support, etc.):

- "Allow users to reset password" → feature
- "Add email notifications" → feature
- "Implement dark mode" → feature

**Default**: If unclear, classify as **feature**.

### 3. Generate Name

Create a kebab-case name from the description:

- "Fix timeout on login page" → "login-timeout"
- "Allow users to reset password" → "user-password-reset"

### 4. Execute Init Script

Run:

```bash
python .ai-workflow/scripts/init-workflow.py "{name}" "{description}" --type {type}
```

### 5. Confirm to User

**Example for bug:**

```
✓ Classified as: bug
✓ Bug initialized: login-timeout

Created: .ai-workflow/bugs/login-timeout/
Status: reported

Next steps:
  1. /ai.add-context login-timeout — add relevant codebase context (optional)
  2. /ai.triage-bug login-timeout — diagnose root cause and plan fix
```

**Example for feature:**

```
✓ Classified as: feature
✓ Feature initialized: user-password-reset

Created: .ai-workflow/features/user-password-reset/
Status: clarifying

Next steps:
  1. /ai.add-context user-password-reset — add relevant codebase context
  2. /ai.clarify user-password-reset — start requirements clarification
```

### 6. STOP AND WAIT

**IMPORTANT: Your task ends here.**

**Do NOT continue to the next steps automatically:**

- Do NOT run `/ai.add-context`
- Do NOT run `/ai.clarify`
- Do NOT run `/ai.triage-bug`
- Do NOT start implementing or coding
- Do NOT ask follow-up questions about the workflow

**Wait for the user to explicitly run one of the suggested next commands.**

This is a step-by-step workflow where each command must be explicitly invoked by the user. Your role was to classify and initialize the workflow. The user will decide when to proceed.

---

## Example

**User:**

```
/ai.add Fix timeout on login page
```

**AI classifies:** bug (keyword "Fix")

**AI executes:**

```bash
python .ai-workflow/scripts/init-workflow.py "login-timeout" "Fix timeout on login page" --type bug
```

**AI responds:**

```
✓ Classified as: bug
✓ Bug initialized: login-timeout

Created: .ai-workflow/bugs/login-timeout/
├── state.yml (status: reported)
├── report.md
├── context.md
├── clarifications/
├── triage.md (pending)
└── fix-plan.md (pending)

Next steps:
  1. /ai.add-context login-timeout — add relevant codebase context (optional)
  2. /ai.triage-bug login-timeout — diagnose root cause and plan fix
```
