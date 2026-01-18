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
│   ├── ai.add.prompt.md                      # Unified /ai.add with clarifications + PRD generation (all-in-one)
│   ├── ai.clarify.prompt.md                  # Post-PRD refinement through Q&A and direct updates
│   ├── ai.define-coding-instructions.prompt.md  # Define coding standards
│   ├── ai.define-idea.prompt.md              # Idea refinement and exploration
│   ├── ai.define-implementation-plan.prompt.md  # Create implementation plan
│   ├── ai.define-tech-stack.prompt.md        # Define global tech stack
│   ├── ai.execute.prompt.md                  # Execute implementation plan
│   ├── ai.help.prompt.md                     # Show workflow status and next steps
│   ├── ai.plan-fix.prompt.md                 # Lightweight bug fix planning
│   ├── ai.set-current.prompt.md              # Set current workflow context
│   ├── ai.triage-bug.prompt.md               # Bug diagnosis and root cause
│   └── ai.verify.prompt.md                   # Verify implementation plan or code
└── scripts/               # Python utilities
    ├── config.py          # Config loader with workflow type support
    ├── init-workflow.py   # Generic workflow initialization (feature/bug/etc.)
    ├── init-impl-plan.py  # Create implementation plan structure
    └── update-plan-state.py  # Update plan state during execution

.ai-workflow/features/     # Feature workflow storage
└── {feature-name}/
    ├── state.yml          # Status tracking
    ├── request.md         # Original description + clarifications (## Clarifications section)
    ├── context.md         # User-curated codebase context
    ├── prd.md            # Generated requirements doc (created via /ai.create-prd)
    └── implementation-plan/
        ├── plan-state.yml
        └── plan.md

.ai-workflow/bugs/         # Bug workflow storage
└── {bug-name}/
    ├── state.yml          # Bug status tracking
    ├── report.md          # Bug description and reproduction steps
    ├── context.md         # Relevant codebase context (optional)
    ├── triage.md          # Root cause diagnosis and fix approach
    └── fix-plan.md        # Lightweight fix implementation checklist

.ai-workflow/ideas/        # Idea workflow storage
└── {idea-name}/
    ├── state.yml          # Idea status tracking
    ├── description.md     # Original idea description
    ├── context.md         # Optional context
    ├── refinement/        # Refinement rounds (iterative Q&A)
    │   └── round-{n}.md
    └── refined-idea.md    # Synthesized idea document (after refinement)
```

### Global Context Files

```text
.ai-workflow/memory/
├── tech-stack.md          # Global technology stack definition
└── coding-rules/          # Coding standards and best practices
    ├── index.md           # Entry point listing all rule categories
    ├── {category}/        # Category-specific rules
    │   ├── index.md       # Category overview and rule listing
    │   └── {rule}.md      # Individual rule files
    └── ...
```

**Tech Stack** (`tech-stack.md`):

- Defines technologies, versions, and integrations used across the project
- Created via `/ai.define-tech-stack` command through guided wizard questions
- Automatically included when creating PRDs and implementation plans
- Updated as technology choices evolve
- Provides consistent tech context for all features

**Coding Rules** (`coding-rules/`):

- Collection of coding standards organized by category (e.g., react/, typescript/, testing/)
- User-maintained manually (no creation prompt currently)
- Only included during implementation planning (`/ai.define-implementation-plan`)
- Not included in PRDs (PRDs focus on *what*, coding rules guide *how*)
- Hierarchical structure: index → category index → rule files
- Example categories: component architecture, naming conventions, type safety, testing patterns

### Configuration System

**Config Loader** (`.ai-workflow/scripts/config.py`):

- Auto-discovers `config.yml` by walking up directory tree
- Falls back to defaults if PyYAML not installed
- Supports future polyglot script execution (bash/powershell)

**Key Config Paths**:

- `paths.features`: Location of feature folders (default: `.ai-workflow/features`)
- `paths.bugs`: Location of bug folders (default: `.ai-workflow/bugs`)
- `paths.ideas`: Location of idea folders (default: `.ai-workflow/ideas`)
- `paths.prompts`: Location of prompt templates
- `paths.scripts`: Location of Python scripts
- `defaults.date_format`: Date format for state files (default: `%Y-%m-%d`)
- `defaults.workflow_type`: Default workflow type (default: `feature`)

**Workflow Types**:

- `workflow_types.feature`: Feature workflow configuration (states, artifacts, classification keywords)
- `workflow_types.bug`: Bug workflow configuration (simplified, faster process)
- `workflow_types.idea`: Idea workflow configuration (pre-workflow exploration and refinement)

**Note**: Features, bugs, and ideas are stored in separate folders to maintain clear organization of workflow artifacts.

**Clarification Settings** (`clarification` section):

- `format_version`: Version of clarification format (2.0 = sequential)
- `default_question_count`: Default number of questions to plan (default: 5)
- `allow_followups`: Enable dynamic follow-up questions (default: true)
- `show_progress`: Display progress indicator like "Question 3/5+" (default: true)
- `max_followups_per_round`: Limit follow-ups to prevent question explosion (default: 2)

## Sequential Clarification System

### Overview

The workflow uses a **sequential one-by-one question format** for all clarification-based prompts (`/ai.add`, `/ai.clarify`, `/ai.define-idea`, `/ai.triage-bug`). Instead of asking multiple questions at once, the AI asks ONE question at a time with THREE predefined options (A, B, C) plus the ability to provide a custom answer.

**Note on Unified `/ai.add` Workflow:**

The sequential clarification format is used in two contexts:
1. **During `/ai.add`** for initial feature/bug creation - answers are appended to `request.md` under `## Clarifications` section (features only; bugs skip storage)
2. **During `/ai.clarify`** for post-PRD refinement - answers are stored in conversation history, proposed changes shown to user, then PRD updated directly

### Question Format (Standardized)

```
Question {n}/{total}+

{Question text}

Options:
  A: {First approach/scenario}
  B: {Second approach/scenario}
  C: {Third approach/scenario}

Recommendation: {Option X}, because {clear reasoning}

---
You can select A, B, or C, or provide your own answer.
```

### Round File Format with Metadata

All clarification rounds now include metadata for state tracking:

```markdown
# [Clarification|Refinement] Round {n}

<!-- METADATA
format_version: 2.0
round_type: sequential
planned_questions: 5
current_question: 3
allow_followups: true
-->

## Date
{YYYY-MM-DD}

## Questions & Answers

### Q1: {question text}
**Options:**
- A: {option A}
- B: {option B}
- C: {option C}

**Recommendation:** {Option X}, because {reasoning}

**Answer:** {user's answer (A/B/C or custom text)}

### Q2: {question text}
...
```

**Metadata Fields:**

- `format_version`: "2.0" indicates sequential format
- `round_type`: "sequential" (vs legacy batch format)
- `planned_questions`: Total number of questions planned for this round
- `current_question`: Last answered question number (for resumption)
- `allow_followups`: Whether dynamic follow-ups are allowed

### Resumption Logic

If a clarification session is interrupted, the AI can resume by:

1. Reading the round file
2. Parsing metadata to find `current_question`
3. Continuing from `current_question + 1`

Example:

```
Resuming refinement/round-01 (continuing from Question 3/5)...

Question 4/5+
...
```

### Hybrid Question Approach

The system uses a **hybrid approach**:

- AI plans initial questions upfront (e.g., 5 questions)
- Can add follow-up questions dynamically based on answers
- Progress shown as "Question 3/5+" (the "+" indicates potential additional questions)

### Option Generation Guidelines

Options are generated based on **common industry patterns** (priority) and different solution approaches (secondary):

**For Features (/clarify):**

- Research typical solutions from similar projects
- Check context.md for tech stack hints
- Present 3 most common approaches with trade-offs

**For Ideas (/define-idea):**

- Present problem/solution scenarios
- Use evidence levels (strong/moderate/assumption-based)
- Support exploration without being judgmental

**For Bugs (/triage-bug):**

- Present diagnostic scenarios
- Use common failure patterns
- Help narrow down root cause

### Backward Compatibility

- **Old format rounds** (multi-question, no metadata) remain valid
- **New format rounds** (sequential, with metadata) are created for new sessions
- Both formats coexist without migration needed
- AI detects format by checking for metadata in round file

### Examples

**Feature Clarification (/clarify):**

```
Question 1/5+

Should users be able to reset their password?

Options:
  A: Yes, via email link (most common, secure)
  B: Yes, via SMS code (faster, requires phone number)
  C: Yes, both email and SMS options (maximum flexibility)

Recommendation: Option A, because email-based password reset is the industry
standard, requires no additional PII (phone numbers), and provides better
security with time-limited tokens.

---
You can select A, B, or C, or provide your own answer.
```

**Idea Refinement (/ai.define-idea Round 1):**

```
Question 1/5+

What specific problem does this idea primarily address?

Options:
  A: User pain point - users struggling with current workflow or process
  B: Business opportunity - potential for revenue or competitive advantage
  C: Technical improvement - reducing technical debt or improving maintainability

Recommendation: Option A, because ideas grounded in user pain points typically
have clearer adoption metrics and measurable impact on user satisfaction.

---
You can select A, B, or C, or provide your own answer.
```

**Bug Triage (/triage-bug):**

```
Question 1/3

How consistently does the login timeout occur?

Options:
  A: Happens every time for all users (100% reproducible)
  B: Happens intermittently, roughly 20-50% of attempts
  C: Happens only under specific conditions (certain users, times, or actions)

Recommendation: Understanding consistency helps identify the failure type. Option A
suggests a code-level bug or configuration error, Option B suggests resource contention
or race conditions, Option C suggests environment-specific or data-dependent issues.

---
You can select A, B, or C, or provide your own answer.
```

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
/ai.add Fix timeout on login page           → Bug
/ai.add Allow users to reset password       → Feature
/ai.add Login button is broken              → Bug
/ai.add Implement dark mode                 → Feature
```

### Global Context Commands

| Command                       | Type   | Purpose                                      | Script Invoked |
|-------------------------------|--------|----------------------------------------------|----------------|
| `/ai.define-tech-stack`          | Prompt | Define global tech stack through wizard Q&A | None           |
| `/ai.define-coding-instructions` | Prompt | Define coding instructions and standards through Q&A | None           |

**Note**: Tech stack and coding instructions are automatically included in implementation plans once defined. Tech stack is also included in PRDs.

### Verification Command

| Command          | Type   | Purpose                                                           | Script Invoked |
|------------------|--------|-------------------------------------------------------------------|----------------|
| `/ai.verify`        | Prompt | Verify plan/code against coding standards (uses current context) | None           |
| `/ai.verify {name}` | Prompt | Verify specific workflow against coding standards                | None           |

**Note**: Verification analyzes implementation plans or actual code against coding standards defined in `.ai-workflow/memory/coding-rules/`. Reports are saved in `.ai-workflow/reports/` with timestamp history. This is a read-only operation that does not modify any files.

### Feature Workflow Commands

| Command | Type | Purpose | Script Invoked |
|---------|------|---------|----------------|
| `/ai.create-prd {name}` | Prompt | Generate PRD from clarified requirements | None |
| `/ai.clarify {name}` | Prompt | Refine existing PRD through Q&A and direct updates | None |
| `/define-implementation-plan {name}` | Prompt→Script | Create implementation plan | `init-impl-plan.py` |
| `/ai.execute {name}` | Prompt→Script | Execute implementation plan | `update-plan-state.py` |

**Note**: Features are created with `/ai.add` which handles initialization and clarifications. PRD generation is a separate step via `/ai.create-prd`. Use `/ai.clarify` for PRD refinements after the PRD exists.

### Bug Workflow Commands

| Command | Type | Purpose | Script Invoked |
|---------|------|---------|----------------|
| `/ai.add {description}` | Prompt→Script | Initialize bug with inline clarifications (AI-detected) | `init-workflow.py` |
| `/ai.triage-bug {name}` | Prompt | Diagnose root cause | None |
| `/ai.plan-fix {name}` | Prompt | Create lightweight fix checklist | None |

**Note**: Bugs are created with inline clarifications during `/ai.add`. Unlike features, bugs skip PRD generation and proceed directly to triage.

### Idea Workflow Commands

| Command | Type | Purpose | Script Invoked |
|---------|------|---------|----------------|
| `/ai.define-idea {description}` | Prompt→Script | Initialize and refine idea through Q&A | `init-workflow.py` |
| `/ai.define-idea {name}` | Prompt | Continue refinement rounds | None |
| `/ai.add-context {name}` | Prompt | Add context (optional) | None |
| `/ai.clarify {name}` | Prompt | Additional clarification (optional) | None |

**Note**: Ideas are standalone and don't auto-classify. Users explicitly create ideas with `/ai.define-idea` instead of `/add`.

### Execution Pattern

**New unified `/add` command:**

When AI receives `/ai.add "Fix timeout on login page"`:

1. AI reads `.ai-workflow/prompts/add.md`
2. Classifies description → detects "Fix" keyword → type = bug
3. Generates name: "login-timeout"
4. Executes `python .ai-workflow/scripts/init-workflow.py "login-timeout" "Fix timeout on login page" --type bug`
5. Script creates bug folder in `.ai-workflow/bugs/login-timeout/`
6. AI confirms completion and suggests next steps

## State Management

### Workflow Types

The system supports three workflow types:

1. **Feature Workflow** (`.ai-workflow/features/`)
2. **Bug Workflow** (`.ai-workflow/bugs/`)
3. **Idea Workflow** (`.ai-workflow/ideas/`)

### Feature States

Features transition through these states:

```
clarifying → clarified → prd-draft → prd-approved → planning → in-progress
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

### Idea States

Ideas transition through these states:

```
exploring → refined → shelved → converted
```

**state.yml** tracks:

- `workflow_type`: Type of workflow (idea)
- `name`: Idea name (kebab-case)
- `status`: Current state
- `created`: Creation date
- `updated`: Last modification date
- `converted_to`: If converted, stores "feature:{name}" or "bug:{name}"

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
2. **Manual**: Use `/ai.set-current {name}` to switch context at any time

**Using Current Context:**

All workflow commands support optional parameters - you can omit the workflow name and they'll use the current context:

```
/ai.clarify              # Uses current context
/ai.clarify user-auth    # Explicit override
```

### Commands Supporting Current Context

All follow-up commands support optional workflow names:

- `/ai.clarify` → `/ai.clarify {name}`
- `/ai.create-prd` → `/ai.create-prd {name}` (features only)
- `/ai.update-feature` → `/ai.update-feature {name}` (features only)
- `/ai.define-implementation-plan` → `/define-implementation-plan {name}` (features only)
- `/ai.execute` → `/ai.execute {name}` (features only)
- `/ai.triage-bug` → `/ai.triage-bug {name}` (bugs only)
- `/ai.plan-fix` → `/ai.plan-fix {name}` (bugs only)
- `/ai.define-idea` → `/ai.define-idea {name}` (ideas only)

### Global State Structure

```yaml
version: 1
current:
  name: user-auth           # Current workflow name
  workflow_type: feature    # "feature" | "bug" | "idea"
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
- Example: `/ai.clarify feature-a` while current context is `feature-b`

**Context Switching:**

- Use `/ai.set-current {name}` to switch between workflows
- Explicit parameters always override current context

**Multi-Terminal Usage:**

- Current context is per-workspace (stored in `.ai-workflow/memory/`)
- Last write wins if multiple terminals modify the same workspace
- Use explicit parameters for parallel work across terminals

## Key Design Principles

1. **User Controls Each Step**: No autonomous execution—user explicitly runs each command
2. **Context Over Automation**: User provides context during workflow creation; AI doesn't scan codebase automatically
3. **Agent-Agnostic**: Works via copy-paste with any LLM (Claude, Copilot, etc.)
4. **Version Controlled**: All artifacts (PRDs, clarifications) stored in git alongside code
5. **Deterministic Scripts**: File operations use Python scripts for consistency
6. **Cognitive Prompts**: Synthesis/analysis tasks handled by AI via prompts
7. **Global Context Awareness**: Tech stack and coding rules provide consistent guardrails across all features

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

1. Create `.ai-workflow/prompts/ai.{command-name}.prompt.md`
2. Follow existing structure: Purpose, Usage, Instructions, Examples

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

| Aspect | Feature Workflow | Bug Workflow | Idea Workflow |
|--------|------------------|--------------|---------------|
| **Command** | `/ai.add "Add X"` | `/ai.add "Fix X"` (auto-detected) | `/ai.define-idea "description"` (explicit) |
| **States** | clarifying → clarified → prd-draft → prd-approved → planning → in-progress | reported → triaged → fixing → resolved → closed | exploring → refined → shelved/converted |
| **Storage** | `.ai-workflow/features/{name}/` | `.ai-workflow/bugs/{name}/` | `.ai-workflow/ideas/{name}/` |
| **PRD Required** | ✓ Yes (via `/ai.create-prd`) | ✗ No (skip PRD) | ✗ No (refined-idea.md instead) |
| **Context** | ✓ Gathered during /ai.add (optional) | ✓ Gathered during /ai.add (optional) | ✓ context.md (optional) |
| **Clarifications** | ✓ Inline during `/ai.add` (appended to request.md) | ✓ Inline during `/ai.add` (conversation-based) | ✓ refinement/ rounds (2-3 typical) |
| **Planning** | Multi-phase implementation-plan/ | Simple fix-plan.md checklist | ✗ No (pre-workflow exploration) |
| **Verification** | ✓ /ai.verify (plan and code) | ✓ /ai.verify (fix-plan and code) | ✗ No verification support |
| **Main Flow** | add (with inline clarify) → create-prd → approve → plan → execute | add (with inline clarify) → triage → plan-fix | define-idea (multi-round) → synthesize → convert to feature/bug |

## Common Workflows

### Creating a Feature

```
/ai.add "Add user profile with avatar upload"
# AI classifies as feature, creates .ai-workflow/features/user-profile/
# AI asks: "Would you like to provide codebase context?" (yes/no)
# (Optional) User provides context - AI organizes into context.md
# AI asks clarification questions one-by-one (5-7 questions)
# User answers each question
# AI appends clarifications to request.md
# Feature initialized and clarified!

/ai.create-prd user-profile
# AI reads request.md (includes clarifications), context.md
# AI generates prd.md from all sources
# PRD created!

# Review prd.md

# Optional: if changes needed after reviewing PRD
/ai.clarify user-profile
# AI reads PRD, asks clarifying questions
# AI shows proposed changes
# User confirms
# AI updates prd.md directly

# When PRD is approved
# Update state.yml status to 'prd-approved'

/ai.define-implementation-plan user-profile
# AI creates multi-phase implementation plan

/ai.execute user-profile
# Choose: single phase or entire plan
# AI implements tasks exactly as specified in plan
# Updates plan-state.yml after completion
```

### Creating a Bug Fix

```
/ai.add "Fix timeout on login page"
# AI classifies as bug, creates .ai-workflow/bugs/login-timeout/
# AI asks: "Would you like to provide codebase context?" (yes/no)
# (Optional) User provides authentication logic, session files

/ai.triage-bug login-timeout
# AI asks diagnostic questions, identifies root cause

/ai.plan-fix login-timeout
# AI creates lightweight fix checklist
# Ready to implement!
```

### Creating an Idea

```
/ai.define-idea "Add AI-powered search to documentation"
# AI creates .ai-workflow/ideas/ai-powered-search/
# AI asks clarifying questions about problem, context, success criteria
# User answers

/ai.define-idea ai-powered-search
# Round 2: AI tests assumptions, explores alternatives
# User responds with thoughts

# AI offers to synthesize
synthesize

# AI creates refined-idea.md with:
# - Problem/solution analysis
# - Assumptions tested (desirability, viability, feasibility, usability, risks)
# - Alternatives considered
# - Recommended next steps

# User decides:
/ai.add "Implement semantic search based on ai-powered-search idea"
# Or: shelve for later, do more research, etc.
```

### Verifying Implementation

```
# Verify implementation plan against coding standards (after planning)
/ai.verify user-profile
# AI reads plan and coding standards
# AI generates report in .ai-workflow/reports/

# Verify actual code against plan and standards (after execution)
/ai.verify user-profile code
# Provide file paths when prompted
# AI analyzes code and generates detailed report

# Reports are timestamped for history
# View latest: .ai-workflow/reports/verification-user-profile-latest.report.md
```

### Defining Tech Stack (One-Time Setup)

```
/ai.define-tech-stack
# AI asks sequential questions about your tech stack:
# - Primary language and version
# - Frontend framework
# - Backend framework
# - Database(s)
# - External services
# - Hosting/deployment
# - Testing frameworks
# Answer questions (select A/B/C or provide custom answers)

# AI creates .ai-workflow/memory/tech-stack.md

# Review and update as needed
/ai.define-tech-stack
# Choose "Update existing" to make changes
```

### Defining Coding Instructions (One-Time Setup)

```
/ai.define-coding-instructions
# AI asks sequential questions about coding standards:
# - Development methodology (TDD/BDD/etc.)
# - Testing coverage philosophy
# - Architectural principles (SOLID, DRY, etc.)
# - Code review standards
# - Documentation standards
# - Additional standards
# Answer questions (select A/B/C or provide custom answers)

# AI creates .ai-workflow/memory/coding-rules/index.md

# Review and update as needed
/ai.define-coding-instructions
# Choose "Update existing" to make changes
```

**Note**: After creating the base index.md, you can manually add category-specific rules:

```
# Create category directories manually
mkdir -p .ai-workflow/memory/coding-rules/react
mkdir -p .ai-workflow/memory/coding-rules/typescript

# Create category indices (e.g., .ai-workflow/memory/coding-rules/react/index.md)
# Add rule files (e.g., .ai-workflow/memory/coding-rules/react/component-architecture.md)
# Link categories in the main index.md

# Category-specific rules will automatically be referenced in implementation plans
```

## Notes for Future Claude Instances

- **Use `/add` command**: New unified command that auto-classifies features vs bugs
- **AI Classification**: Analyze description for keywords (fix/bug/error → bug; add/implement/create → feature)
- **Idea workflow is separate**: Ideas use `/ai.define-idea` command, not `/add` - they're pre-workflow exploration
- **Don't auto-scan codebases**: Prompt user for context during `/ai.add`, but don't automatically scan
- **Prompt files are instructions**: Read them fully before executing commands
- **State transitions matter**: Check `state.yml` before running commands (e.g., PRD must exist before implementation plan)
- **Workflow-specific states**: Features, bugs, and ideas each have different state transitions (see State Management section)
- **Item names are kebab-case**: Scripts normalize automatically
- **"TBD" is valid**: Better to acknowledge missing info than invent details
- **Scripts must be invoked from project root**: Config loader walks up from cwd to find `.ai-workflow/config.yml`
- **Bug workflow is lighter**: No PRD required, simpler planning, optional context/clarifications
- **Idea workflow is exploratory**: Focuses on refinement and assumption testing, not implementation. Ideas can be converted to features/bugs when ready
