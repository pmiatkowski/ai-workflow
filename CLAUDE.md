# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

The AI Feature Workflow is a structured, agent-agnostic system for adding features to existing codebases through prompt-driven development. It enforces a predictable workflow from initial feature request through PRD creation to implementation planning, with all artifacts stored in version control.

## Architecture

### Hybrid Prompt-Script Model

The system uses a hybrid approach where:
- **Prompts** (`.ai-workflow/prompts/*.md`) contain AI instructions for cognitive tasks (Q&A, synthesis, analysis)
- **Scripts** (`.ai-workflow/scripts/*.py`) handle deterministic file system operations
- **AI agents** read prompts, invoke scripts when needed, and guide users through the workflow

### Directory Structure

```
.ai-workflow/
├── config.yml              # Central configuration with workflow types
├── prompts/               # AI instruction templates
│   ├── add.md             # Unified /add command with AI classification
│   ├── add-feature.md     # Legacy feature command (still supported)
│   ├── add-context.md
│   ├── clarify.md
│   ├── create-prd.md
│   ├── update-feature.md
│   ├── define-implementation-plan.md
│   ├── execute.md         # Execute implementation plan
│   ├── triage-bug.md      # Bug diagnosis and root cause
│   └── plan-fix.md        # Lightweight bug fix planning
└── scripts/               # Python utilities
    ├── config.py          # Config loader with workflow type support
    ├── init-workflow.py   # Generic workflow initialization (feature/bug/etc.)
    ├── init-feature.py    # Legacy wrapper (delegates to init-workflow.py)
    ├── init-impl-plan.py  # Create implementation plan structure
    └── update-plan-state.py  # Update plan state during execution

.ai-workflow/features/     # Feature workflow storage
└── {feature-name}/
    ├── state.yml          # Status tracking
    ├── request.md         # Original description
    ├── context.md         # User-curated codebase context
    ├── clarifications/    # Q&A rounds
    │   └── round-{n}.md
    ├── prd.md            # Generated requirements doc
    ├── updates/          # Post-PRD change records
    │   └── update-{n}.md
    └── implementation-plan/
        ├── plan-state.yml
        └── plan.md

.ai-workflow/bugs/         # Bug workflow storage
└── {bug-name}/
    ├── state.yml          # Bug status tracking
    ├── report.md          # Bug description and reproduction steps
    ├── context.md         # Relevant codebase context (optional)
    ├── clarifications/    # Optional Q&A rounds (if needed)
    │   └── round-{n}.md
    ├── triage.md          # Root cause diagnosis and fix approach
    └── fix-plan.md        # Lightweight fix implementation checklist
```

### Configuration System

**Config Loader** (`.ai-workflow/scripts/config.py`):
- Auto-discovers `config.yml` by walking up directory tree
- Falls back to defaults if PyYAML not installed
- Supports future polyglot script execution (bash/powershell)

**Key Config Paths**:
- `paths.features`: Location of feature folders (default: `.ai-workflow/features`)
- `paths.bugs`: Location of bug folders (default: `.ai-workflow/bugs`)
- `paths.prompts`: Location of prompt templates
- `paths.scripts`: Location of Python scripts
- `defaults.date_format`: Date format for state files (default: `%Y-%m-%d`)
- `defaults.workflow_type`: Default workflow type (default: `feature`)

**Workflow Types**:
- `workflow_types.feature`: Feature workflow configuration (states, artifacts, classification keywords)
- `workflow_types.bug`: Bug workflow configuration (simplified, faster process)

**Note**: Features and bugs are stored in separate folders to maintain clear organization of workflow artifacts.

## Workflow Commands

All commands are prompts that users paste into AI agents. Scripts are invoked automatically by AI when needed.

### Unified Command (Recommended)

| Command | Type | Purpose | Script Invoked |
|---------|------|---------|----------------|
| `/add {description}` | Prompt→Script | Add work item (AI classifies as feature/bug) | `init-workflow.py` |

**AI Classification:**
- **Bug keywords**: fix, bug, error, broken, crash, issue, failing, timeout → Creates bug
- **Feature keywords**: add, implement, create, allow, enable, support → Creates feature
- **Default**: If unclear, classifies as feature

**Examples:**
```
/add Fix timeout on login page           → Bug
/add Allow users to reset password       → Feature
/add Login button is broken              → Bug
/add Implement dark mode                 → Feature
```

### Feature Workflow Commands

| Command | Type | Purpose | Script Invoked |
|---------|------|---------|----------------|
| `/add-feature {name} {desc}` | Prompt→Script | Initialize feature folder (explicit) | `init-feature.py` → `init-workflow.py` |
| `/add-context {name}` | Prompt | Add codebase/business context | None |
| `/clarify {name}` | Prompt | Requirements Q&A | None |
| `/create-prd {name}` | Prompt | Synthesize PRD | None |
| `/update-feature {name}` | Prompt | Handle post-PRD changes | None |
| `/define-implementation-plan {name}` | Prompt→Script | Create implementation plan | `init-impl-plan.py` |
| `/execute {name}` | Prompt→Script | Execute implementation plan | `update-plan-state.py` |

### Bug Workflow Commands

| Command | Type | Purpose | Script Invoked |
|---------|------|---------|----------------|
| `/add {description}` | Prompt→Script | Initialize bug (AI-detected) | `init-workflow.py` |
| `/add-context {name}` | Prompt | Add codebase context (optional) | None |
| `/clarify {name}` | Prompt | Clarification Q&A (optional) | None |
| `/triage-bug {name}` | Prompt | Diagnose root cause | None |
| `/plan-fix {name}` | Prompt | Create lightweight fix checklist | None |

### Execution Pattern

**New unified `/add` command:**

When AI receives `/add "Fix timeout on login page"`:

1. AI reads `.ai-workflow/prompts/add.md`
2. Classifies description → detects "Fix" keyword → type = bug
3. Generates name: "login-timeout"
4. Executes `python .ai-workflow/scripts/init-workflow.py "login-timeout" "Fix timeout on login page" --type bug`
5. Script creates bug folder in `.ai-workflow/bugs/login-timeout/`
6. AI confirms completion and suggests next steps

**Legacy `/add-feature` command (still supported):**

When AI receives `/add-feature user-auth "Allow login with email/password"`:

1. AI reads `.ai-workflow/prompts/add-feature.md`
2. Follows instructions to execute `python .ai-workflow/scripts/init-feature.py "user-auth" "Allow login with email/password"`
3. `init-feature.py` delegates to `init-workflow.py --type feature`
4. Script creates feature folder in `.ai-workflow/features/user-auth/`
5. AI confirms completion and suggests next steps

## State Management

### Workflow Types

The system supports two workflow types:

1. **Feature Workflow** (`.ai-workflow/features/`)
2. **Bug Workflow** (`.ai-workflow/bugs/`)

### Feature States

Features transition through these states:

```
clarifying → prd-draft → prd-approved → planning → in-progress
```

**state.yml** tracks:
- `workflow_type`: Type of workflow (feature)
- `name`: Item name (kebab-case)
- `status`: Current state
- `created`: Creation date
- `updated`: Last modification date

### Bug States

Bugs transition through these states:

```
reported → triaged → fixing → resolved → closed
```

**state.yml** tracks:
- `workflow_type`: Type of workflow (bug)
- `name`: Bug name (kebab-case)
- `status`: Current state
- `created`: Creation date
- `updated`: Last modification date

### Implementation Plan States

**plan-state.yml** tracks:
- `status`: Plan status (pending/in-progress/completed)
- `current_phase`: Phase number being worked on
- `phases`: List of phase identifiers

## Global Memory System

The workflow maintains a "current" feature or bug in `.ai-workflow/memory/global-state.yml`. This allows commands to work without requiring explicit names, streamlining the workflow for focused development.

### Current Context Tracking

**Setting Current Context:**

1. **Automatic**: When you create a new feature/bug with `/add`, it automatically becomes current
2. **Manual**: Use `/set-current {name}` to switch context at any time

**Using Current Context:**

All workflow commands support optional parameters - you can omit the workflow name and they'll use the current context:

```
/clarify              # Uses current context
/clarify user-auth    # Explicit override
```

### Commands Supporting Current Context

All follow-up commands support optional workflow names:

- `/add-context` → `/add-context {name}`
- `/clarify` → `/clarify {name}`
- `/create-prd` → `/create-prd {name}` (features only)
- `/update-feature` → `/update-feature {name}` (features only)
- `/define-implementation-plan` → `/define-implementation-plan {name}` (features only)
- `/execute` → `/execute {name}` (features only)
- `/triage-bug` → `/triage-bug {name}` (bugs only)
- `/plan-fix` → `/plan-fix {name}` (bugs only)

### Global State Structure

```yaml
version: 1
current:
  name: user-auth           # Current workflow name
  workflow_type: feature    # "feature" | "bug"
  set_date: 2025-12-28      # When context was set
  set_method: manual        # "auto" | "manual"
last_updated: 2025-12-28
```

### Workflow Type Validation

Commands validate workflow types automatically:

- Feature-only commands (create-prd, update-feature, define-implementation-plan, execute) will error if current context is a bug
- Bug-only commands (triage-bug, plan-fix) will error if current context is a feature
- Universal commands (add-context, clarify) work with both types

### Best Practices

**Single Feature/Bug Focus:**
- Current context works best when focusing on one item at a time
- The system auto-updates when you create new items with `/add`

**Multiple Workflows:**
- When working on multiple items simultaneously, use explicit parameters
- Example: `/clarify feature-a` while current context is `feature-b`

**Context Switching:**
- Use `/set-current {name}` to switch between workflows
- Explicit parameters always override current context

**Multi-Terminal Usage:**
- Current context is per-workspace (stored in `.ai-workflow/memory/`)
- Last write wins if multiple terminals modify the same workspace
- Use explicit parameters for parallel work across terminals

## Key Design Principles

1. **User Controls Each Step**: No autonomous execution—user explicitly runs each command
2. **Context Over Automation**: User provides context; AI doesn't scan codebase automatically
3. **Agent-Agnostic**: Works via copy-paste with any LLM (Claude, Copilot, etc.)
4. **Version Controlled**: All artifacts (PRDs, clarifications) stored in git alongside code
5. **Deterministic Scripts**: File operations use Python scripts for consistency
6. **Cognitive Prompts**: Synthesis/analysis tasks handled by AI via prompts

## PRD Format

PRDs follow a strict template enforced by `create-prd.md`:

**Required Sections**:
- Overview (one-paragraph summary)
- Problem Statement
- Goals (measurable if possible)
- Non-Goals (explicit scope limits)
- Functional Requirements (numbered FR-1, FR-2, etc.)
- Technical Considerations
- Acceptance Criteria (checkbox format)
- Open Questions (or "None")

**Optional Sections**:
- User Stories

**Rules**:
- Use "TBD" if information missing—never omit sections
- Focus on *what*, not *how* (avoid implementation details)
- Synthesize from clarifications, don't just copy
- Resolve contradictions or mark as unresolved

## Scripts

### Running Scripts Manually

While AI typically invokes scripts, they can be run directly:

```bash
# Initialize workflow item (generic)
python .ai-workflow/scripts/init-workflow.py "item-name" "Description here" --type feature
python .ai-workflow/scripts/init-workflow.py "bug-name" "Description here" --type bug

# Initialize feature (legacy, delegates to init-workflow.py)
python .ai-workflow/scripts/init-feature.py "feature-name" "Description here"

# Initialize implementation plan
python .ai-workflow/scripts/init-impl-plan.py "feature-name"

# View current config
python .ai-workflow/scripts/config.py
```

### Script Conventions

- **Kebab-case conversion**: Feature names automatically normalized
- **Date formatting**: Uses `config.yml` date format
- **Exit codes**: Non-zero on errors (feature exists, PRD missing, etc.)
- **Idempotency**: Scripts fail gracefully if structure already exists

## Working with This Codebase

### Adding New Prompts

1. Create `.ai-workflow/prompts/{command-name}.md`
2. Follow existing structure: Purpose, Usage, Instructions, Examples
3. Update README.md commands table

### Adding New Scripts

1. Create `.ai-workflow/scripts/{script-name}.py` with `#!/usr/bin/env python3`
2. Import config: `from config import cfg`
3. Include fallback config for standalone execution
4. Make executable: `chmod +x .ai-workflow/scripts/{script-name}.py`

### Future Polyglot Support

Config supports `runner: python | bash | powershell` for future expansion:

```
scripts/
  run.py              # dispatcher based on config.runner
  impl/
    python/
      init-feature.py
    bash/
      init-feature.sh
    powershell/
      init-feature.ps1
```

## Dependencies

**Required**:
- Python 3.6+

**Optional**:
- PyYAML (`pip install pyyaml`) — for config loading; falls back to defaults if missing

## Workflow Comparison

| Aspect | Feature Workflow | Bug Workflow |
|--------|------------------|--------------|
| **Command** | `/add "Add X"` or `/add-feature` | `/add "Fix X"` (auto-detected) |
| **States** | clarifying → prd-draft → prd-approved → planning → in-progress | reported → triaged → fixing → resolved → closed |
| **Storage** | `.ai-workflow/features/{name}/` | `.ai-workflow/bugs/{name}/` |
| **PRD Required** | ✓ Yes (full PRD) | ✗ No (skip PRD) |
| **Context** | ✓ context.md (recommended) | ✓ context.md (optional) |
| **Clarifications** | ✓ clarifications/ (multi-round) | ✓ clarifications/ (optional) |
| **Planning** | Multi-phase implementation-plan/ | Simple fix-plan.md checklist |
| **Main Flow** | add → clarify → create-prd → plan → execute | add → triage → plan-fix |

## Common Workflows

### Creating a Feature

```
/add "Add user profile with avatar upload"
# AI classifies as feature, creates .ai-workflow/features/user-profile/

/add-context user-profile
# Provide: relevant models, routes, existing auth system

/clarify user-profile
# Answer AI's questions

/create-prd user-profile
# Review prd.md, update state.yml to prd-approved

/define-implementation-plan user-profile
# AI creates multi-phase implementation plan

/execute user-profile
# Choose: single phase or entire plan
# AI implements tasks exactly as specified in plan
# Updates plan-state.yml after completion
```

### Creating a Bug Fix

```
/add "Fix timeout on login page"
# AI classifies as bug, creates .ai-workflow/bugs/login-timeout/

/add-context login-timeout  # Optional
# Provide: authentication logic, session management files

/triage-bug login-timeout
# AI asks diagnostic questions, identifies root cause

/plan-fix login-timeout
# AI creates lightweight fix checklist
# Ready to implement!
```

### Updating After PRD (Features Only)

```
/update-feature user-profile
# Describe changes
# AI creates updates/update-{n}.md and may trigger new clarification
```

## Notes for Future Claude Instances

- **Use `/add` command**: New unified command that auto-classifies features vs bugs
- **AI Classification**: Analyze description for keywords (fix/bug/error → bug; add/implement/create → feature)
- **Don't auto-scan codebases**: Wait for user to provide context via `/add-context`
- **Prompt files are instructions**: Read them fully before executing commands
- **State transitions matter**: Check `state.yml` before running commands (e.g., PRD must exist before implementation plan)
- **Workflow-specific states**: Features have different states than bugs (see State Management section)
- **Item names are kebab-case**: Scripts normalize automatically
- **"TBD" is valid**: Better to acknowledge missing info than invent details
- **Scripts must be invoked from project root**: Config loader walks up from cwd to find `.ai-workflow/config.yml`
- **Bug workflow is lighter**: No PRD required, simpler planning, optional context/clarifications
