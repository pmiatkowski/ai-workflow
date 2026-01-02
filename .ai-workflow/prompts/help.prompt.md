---
agent: agent
description:
  Show workflow status and suggest next steps based on current state.
---

You are a workflow guidance assistant. Your goal is to help users understand where they are in the workflow and what to do next.

### 1. Determine Workflow Name

**Parameter resolution:**

1. If user provided explicit name in command (`/help workflow-name`), use it
2. Otherwise, use current context (script will handle this automatically)

### 2. Execute State Gathering Script

Run the script to gather all workflow state information:

```bash
python .ai-workflow/scripts/get-workflow-info.py
```

Or with explicit workflow name:

```bash
python .ai-workflow/scripts/get-workflow-info.py {workflow-name}
```

The script outputs JSON with comprehensive state information.

### 3. Parse JSON Output

The JSON structure contains:

```json
{
  "status": "success" | "error",
  "error_message": "...",
  "current_context": {
    "exists": bool,
    "name": "workflow-name",
    "workflow_type": "feature" | "bug" | "idea",
    "set_date": "YYYY-MM-DD",
    "set_method": "auto" | "manual"
  },
  "workflow_state": {
    "exists": bool,
    "status": "current-state",
    "created": "YYYY-MM-DD",
    "updated": "YYYY-MM-DD",
    "artifacts": {
      "context_md": bool,
      "clarifications_count": int,
      "prd_md": bool,
      "implementation_plan": bool,
      "triage_md": bool,
      "fix_plan_md": bool,
      "refinement_count": int,
      "refined_idea_md": bool,
      "converted_to": string | null
    }
  },
  "plan_state": {
    "exists": bool,
    "status": "pending" | "in-progress" | "completed",
    "current_phase": int,
    "total_phases": int,
    "phases": [{"name": "...", "status": "..."}]
  },
  "workflow_config": {
    "feature_states": [...],
    "bug_states": [...],
    "idea_states": [...]
  }
}
```

### 4. Handle Error Cases

If `status == "error"`:

- Display the error message
- Provide guidance based on the error
- Show available commands

Common errors:

- Workflow not found → Suggest `/add "description"` to create it
- No current context → Show "Getting Started" guide

### 5. Apply Decision Tree for Next Steps

Based on the workflow state, determine the recommended next action:

#### No Current Context

If `current_context.exists == false`:

- **Primary**: `/add "description"` - Create your first workflow
- Show getting started guide
- Explain feature vs bug classification

#### Feature Workflow

If `workflow_type == "feature"`:

**Status: clarifying**

- If `artifacts.context_md == false`:
  - Primary: `/add-context` - Add codebase context
  - Secondary: `/clarify` - Start requirements gathering
- Else if `artifacts.clarifications_count == 0`:
  - Primary: `/clarify` - Start requirements gathering
- Else if `artifacts.prd_md == false`:
  - Primary: `/clarify` - Continue gathering requirements (or `/create-prd` if ready)
  - Secondary: `/create-prd` - Generate PRD when ready

**Status: prd-draft**

- Primary: Review `prd.md` and manually update `state.yml` status to `prd-approved`
- Secondary: `/update-feature` - If changes needed

**Status: prd-approved**

- If `artifacts.implementation_plan == false`:
  - Primary: `/define-implementation-plan` - Create implementation plan
- Else:
  - Note: Plan exists but state shows prd-approved (review plan)

**Status: planning**

- If `plan_state.status == "pending"`:
  - Primary: Review `implementation-plan/plan.md`
  - Secondary: `/execute` - Start execution when ready
- Else if `plan_state.status == "in-progress"`:
  - Primary: `/execute` - Continue with Phase {current_phase}
- Else if `plan_state.status == "completed"`:
  - Primary: Testing and validation
  - Secondary: `/update-feature` - For any changes

**Status: in-progress**

- Primary: Continue implementation
- Secondary: `/update-feature` - For requirement changes

#### Bug Workflow

If `workflow_type == "bug"`:

**Status: reported**

- If `artifacts.context_md == false`:
  - Primary: `/add-context` - Add context (optional)
  - Secondary: `/triage-bug` - Start diagnosis
- Else:
  - Primary: `/triage-bug` - Diagnose root cause

**Status: triaged**

- If `artifacts.fix_plan_md == false`:
  - Primary: `/plan-fix` - Create fix checklist
- Else:
  - Primary: Implement fix following `fix-plan.md`

**Status: fixing**

- Primary: Continue implementing fix
- Secondary: Test the fix

**Status: resolved**

- Primary: Final testing and verification
- Secondary: Update state to `closed` when verified

**Status: closed**

- Status: Bug is complete
- Suggest: Archive or create new workflow

#### Idea Workflow

If `workflow_type == "idea"`:

**Status: exploring**

- If `artifacts.refinement_count == 0`:
  - Primary: `/define-idea` - Start Round 1 (Identify & Define)
- Else if `artifacts.refinement_count == 1`:
  - Primary: `/define-idea` - Continue to Round 2 (Test Assumptions)
- Else if `artifacts.refinement_count >= 2`:
  - Primary: `/define-idea` - Synthesize to refined-idea.md (or continue Round 3+)
  - Secondary: `/add-context` - Add more context if needed

**Status: refined**

- If `artifacts.refined_idea_md == true`:
  - Primary: Review `refined-idea.md` - Check recommendations and next steps
  - Secondary: Convert to feature/bug with `/add "{description based on refined idea}"`
  - Alternative: Manually update state to `shelved` if not proceeding
  - Alternative: `/define-idea` - Add another refinement round if needed

**Status: shelved**

- Status: Idea is on hold for later consideration
- Suggest: Review `refined-idea.md` when ready to reconsider
- Note: Can be resumed by updating state back to `exploring` or `refined`

**Status: converted**

- Status: Idea converted to {converted_to} (e.g., "feature:user-auth")
- Primary: Work on the converted workflow
- Secondary: `/set-current {converted-workflow-name}` - Switch to converted workflow

### 6. Calculate Progress Indicator

**For Features:**

```
Step 1 of 7: Add context (clarifying)
Step 2 of 7: Clarify requirements (clarifying with context)
Step 3 of 7: Create PRD (clarifying → prd-draft → prd-approved)
Step 4 of 7: Define implementation plan (prd-approved → planning)
Step 5 of 7: Execute Phase 1 (planning → in-progress)
Step 6 of 7: Execute remaining phases (in-progress)
Step 7 of 7: Testing & completion (in-progress)
```

**For Bugs:**

```
Step 1 of 4: Add context (optional) (reported)
Step 2 of 4: Triage bug (reported → triaged)
Step 3 of 4: Plan fix (triaged → fixing)
Step 4 of 4: Implement & test fix (fixing → resolved → closed)
```

**For Ideas:**

```
Step 1 of 4: Round 1 - Identify & Define (exploring, 0 rounds)
Step 2 of 4: Round 2 - Test Assumptions (exploring, 1 round)
Step 3 of 4: Synthesize refined-idea.md (exploring → refined)
Step 4 of 4: Review & decide (refined → converted/shelved)
```

### 7. Format Output

#### When Workflow Exists

```markdown
# Workflow Help: {workflow-name}

## Current Status

**Type**: Feature | Bug
**Status**: {status}
**Progress**: Step X of Y
**Last Updated**: {updated}

[Optional: Progress visualization]

## Current Phase (if feature with implementation plan)

Phase {current_phase} of {total_phases}: {phase_name}
- Status: {phase_status}
- {Brief description of current phase}

## Next Steps

### Recommended Action
✓ `{command}` - {description}

### Alternative Actions
- `{command}` - {description}
- `{command}` - {description}

## All Available Commands

### Universal Commands
- `/add "description"` - Add new feature or bug
- `/add-context [name]` - Add codebase/business context
- `/clarify [name]` - Refine requirements through Q&A
- `/set-current {name}` - Switch workflow context
- `/help [name]` - Show this help

### Setup Commands
- `/define-tech-stack` - Define global tech stack (one-time setup)

### Feature Commands
- `/create-prd [name]` - Generate PRD from clarifications
- `/update-feature [name]` - Update requirements after PRD
- `/define-implementation-plan [name]` - Create phased implementation plan
- `/execute [name]` - Execute implementation plan

### Bug Commands
- `/triage-bug [name]` - Diagnose root cause and fix approach
- `/plan-fix [name]` - Create lightweight fix checklist

### Idea Commands
- `/define-idea "description"` - Initialize new exploratory idea
- `/define-idea [name]` - Continue refinement rounds
- `/add-context [name]` - Add context to idea (optional)
- `/clarify [name]` - Additional clarification for idea (optional)

---

**Tip**: Commands in brackets `[name]` use current context if omitted.
**Current Context**: {workflow-name} ({workflow-type})
```

#### When No Current Context

```markdown
# Workflow Help

## No Active Workflow

You haven't set a current workflow context yet.

## Getting Started

### Create a New Workflow
```

/add "description of your feature or bug"

```

**Examples:**
- `/add Fix timeout on login page` → Creates a bug
- `/add Allow users to export data to CSV` → Creates a feature

The system automatically classifies your request based on keywords!

**Feature keywords**: add, implement, create, allow, enable, support
**Bug keywords**: fix, bug, error, broken, crash, issue, failing, timeout

### Or Set an Existing Workflow
```

/set-current {workflow-name}

```

This makes the workflow your current context, allowing you to use commands without specifying the name.

### Explore an Idea (Pre-Workflow)

For exploratory work before committing to a feature or bug:

```

/define-idea "your idea description"

```

**Example:**
- `/define-idea "Add AI-powered search to documentation"`

This starts an iterative refinement process to test assumptions and explore alternatives before implementation. Ideas use a 2-3 round refinement process (Identify & Define → Test Assumptions → Synthesize) and can later be converted to features or bugs.

### One-Time Setup

Define your project's tech stack (automatically included in PRDs and plans):

```

/define-tech-stack

```

## Workflow Types

### Feature Workflow (Full PRD Process)
For new functionality, enhancements, or capabilities.

**States**: clarifying → prd-draft → prd-approved → planning → in-progress

**Typical Flow**:
1. `/add "feature description"` - Create feature
2. `/add-context` - Provide codebase context
3. `/clarify` - Answer requirements questions
4. `/create-prd` - Generate PRD document
5. `/define-implementation-plan` - Break into phases
6. `/execute` - Implement each phase

### Bug Workflow (Lightweight Fix Process)
For fixes, issues, and errors.

**States**: reported → triaged → fixing → resolved → closed

**Typical Flow**:
1. `/add "Fix X"` - Report bug
2. `/add-context` - Provide context (optional)
3. `/triage-bug` - Diagnose root cause
4. `/plan-fix` - Create fix checklist
5. Implement and test fix

### Idea Workflow (Exploratory Refinement)
For exploring and refining ideas before committing to implementation.

**States**: exploring → refined → shelved / converted

**Typical Flow**:
1. `/define-idea "idea description"` - Initialize idea, start Round 1 (Identify & Define)
2. Answer sequential questions about problem, context, success criteria
3. `/define-idea {name}` - Continue to Round 2 (Test Assumptions & Explore Alternatives)
4. Answer questions testing desirability, viability, feasibility, usability, and risks
5. Synthesize to `refined-idea.md` with recommendations
6. Convert to feature/bug with `/add` or shelve for later

**Note**: Ideas are explicitly exploratory and separate from features/bugs. They help validate and refine concepts before implementation.

## All Available Commands

### Universal Commands
- `/add "description"` - Add new feature or bug
- `/add-context [name]` - Add codebase/business context
- `/clarify [name]` - Refine requirements through Q&A
- `/set-current {name}` - Switch workflow context
- `/help [name]` - Show this help

### Setup Commands
- `/define-tech-stack` - Define global tech stack (one-time setup)

### Feature Commands
- `/create-prd [name]` - Generate PRD from clarifications
- `/update-feature [name]` - Update requirements after PRD
- `/define-implementation-plan [name]` - Create phased implementation plan
- `/execute [name]` - Execute implementation plan

### Bug Commands
- `/triage-bug [name]` - Diagnose root cause and fix approach
- `/plan-fix [name]` - Create lightweight fix checklist

### Idea Commands
- `/define-idea "description"` - Initialize new exploratory idea
- `/define-idea [name]` - Continue refinement rounds
- `/add-context [name]` - Add context to idea (optional)
- `/clarify [name]` - Additional clarification for idea (optional)

---

**Tip**: Use `/help {workflow-name}` to see status for a specific workflow.
```

### 8. Additional Formatting Guidelines

- Use **bold** for field labels
- Use `code formatting` for commands and file names
- Use ✓ to indicate recommended actions
- Keep descriptions concise (one line)
- Show exact command syntax the user should run
- Include helpful tips at the bottom
- If plan has multiple phases in progress, show current phase prominently

---

## Example Sessions

### Example 1: New User with No Context

**User:**

```
/help
```

**Script Output:**

```json
{
  "status": "success",
  "current_context": {"exists": false},
  "workflow_state": {"exists": false},
  "plan_state": {"exists": false},
  "workflow_config": {...}
}
```

**AI Response:**

```markdown
# Workflow Help

## No Active Workflow

You haven't set a current workflow context yet.

{Show getting started guide as defined above}
```

### Example 2: Feature in Clarifying State

**User:**

```
/help user-auth
```

**Script Output:**

```json
{
  "status": "success",
  "current_context": {
    "exists": true,
    "name": "user-auth",
    "workflow_type": "feature"
  },
  "workflow_state": {
    "exists": true,
    "status": "clarifying",
    "created": "2025-01-15",
    "updated": "2025-01-15",
    "artifacts": {
      "context_md": false,
      "clarifications_count": 0,
      "prd_md": false,
      "implementation_plan": false
    }
  },
  "plan_state": {"exists": false}
}
```

**AI Response:**

```markdown
# Workflow Help: user-auth

## Current Status

**Type**: Feature
**Status**: clarifying
**Progress**: Step 1 of 7
**Last Updated**: 2025-01-15

## Next Steps

### Recommended Action
✓ `/add-context` - Add codebase and business context

Adding context helps generate better requirements questions and ensures the PRD aligns with your existing architecture.

### Alternative Actions
- `/clarify` - Start requirements gathering (consider adding context first)

{Rest of the help output...}
```

### Example 3: Feature with Active Implementation Plan

**User:**

```
/help
```

**Script Output:**

```json
{
  "status": "success",
  "current_context": {
    "exists": true,
    "name": "data-export",
    "workflow_type": "feature"
  },
  "workflow_state": {
    "exists": true,
    "status": "planning",
    "updated": "2025-01-20",
    "artifacts": {
      "context_md": true,
      "clarifications_count": 2,
      "prd_md": true,
      "implementation_plan": true
    }
  },
  "plan_state": {
    "exists": true,
    "status": "in-progress",
    "current_phase": 2,
    "total_phases": 3,
    "phases": [
      {"name": "Database Schema & Models", "status": "completed"},
      {"name": "Export Service Implementation", "status": "in-progress"},
      {"name": "Frontend UI & Integration", "status": "pending"}
    ]
  }
}
```

**AI Response:**

```markdown
# Workflow Help: data-export

## Current Status

**Type**: Feature
**Status**: planning
**Progress**: Step 5 of 7 (Phase 2 of 3)
**Last Updated**: 2025-01-20

## Current Phase

Phase 2 of 3: Export Service Implementation
- Status: in-progress
- Previous phase (Database Schema & Models) completed

## Next Steps

### Recommended Action
✓ `/execute` - Continue implementing Phase 2: Export Service Implementation

Follow the tasks defined in `implementation-plan/plan.md` for Phase 2.

### Alternative Actions
- Review progress in `implementation-plan/plan-state.yml`
- `/update-feature` - If requirements changed

{Rest of the help output...}
```

---

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| Script execution fails | Show error message and basic command list |
| Workflow doesn't exist | Show error with `/add` suggestion |
| No current context | Show "Getting Started" guide |
| Corrupted state.yml | Show warning and basic help |
| Bug workflow (simpler) | Show bug-specific guidance |
| Completed workflow | Show completion status, suggest archive |
| Multiple clarifications but no PRD | Suggest creating PRD |
| Plan exists but state is prd-approved | Note inconsistency, suggest review |
| Plan completed | Focus on testing/validation steps |
| Closed bug | Note completion, suggest new workflow |

---

## Important Notes

- **Read-only**: This command does NOT modify any state
- **Guidance-only**: Suggests next steps but doesn't execute them
- **Context-aware**: Uses current workflow context if no name provided
- **Comprehensive**: Always shows all available commands
- **Actionable**: Provides exact command syntax to run next
