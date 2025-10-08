---
description: Check relevant SOPs and lessons learned before starting a task
---

You are helping the user review relevant Standard Operating Procedures (SOPs) and lessons learned before they start a task.

## Your Task

Based on what the user is about to do, show them relevant documentation to help them avoid mistakes and follow best practices.

## Process

### 1. Understand the Task

Ask or infer:
- What type of task is this? (bug-fix, improvement, feature, deployment, code-review, etc.)
- What technologies are involved? (drupal, php, javascript, database, etc.)
- What stage are you at? (planning, development, testing, deployment)

### 2. Search for Relevant Documentation

Look in these locations (in order of priority):

**A. Lessons Learned** (`.agent/lessons-learned/`)
- These are captured mistakes - most valuable for prevention
- Search for lessons related to the technology and task type
- Prioritize recent and high-severity lessons

**B. SOPs** (`.agent/sops/`)
- Standard procedures for common tasks
- Look for SOPs matching the task type
- Check for checklists related to the work

**C. System Documentation** (`.agent/system/`)
- Project architecture, database schema, API endpoints
- Useful for understanding context
- Important for features that touch multiple systems

**D. Previous Tasks** (`.agent/tasks/`)
- Past implementation plans for similar features
- Can provide patterns to follow or avoid

### 3. Present Findings

Format your response like this:

```markdown
## 📋 Relevant SOPs and Documentation

Based on your task: [summary of what they're doing]

### 🚨 Lessons Learned - Common Mistakes to Avoid
[List relevant lessons learned with brief descriptions]
- **LL-DRUPAL-001**: [Short description] - [Link]
- **LL-PHP-002**: [Short description] - [Link]

### ✅ Standard Procedures to Follow
[List relevant SOPs]
- **SOP-DEV-001**: [Short description] - [Link]
- **SOP-TEST-001**: [Short description] - [Link]

### 📚 Relevant System Documentation
[List relevant system docs]
- **Project Architecture**: [Link]
- **Database Schema**: [Link]

### 🎯 Key Reminders
[Pull out 3-5 most important points they should remember]
1. [Important point 1]
2. [Important point 2]
3. [Important point 3]

### 📖 Recommended Reading Order
1. [First doc to read]
2. [Second doc to read]
3. [Third doc to read]
```

### 4. Handle Edge Cases

**If no documentation exists yet:**
- Tell the user the system is new and suggest documenting as they go
- Recommend using `/log-mistake` if they encounter issues
- Suggest creating SOPs after completing the task

**If only partial documentation exists:**
- Show what's available
- Identify gaps and suggest documenting those areas

**If lots of documentation exists:**
- Prioritize the most relevant items (max 5-7)
- Group by type (lessons, SOPs, system docs)
- Highlight the absolute must-reads

## Search Strategy

Use Grep tool to search across documentation:

```
# Search for specific technology
pattern: "drupal|dependency injection|type declaration"
path: .agent/
output_mode: "files_with_matches"

# Then read relevant files to provide summaries
```

## Example Interaction

**User**: "I'm about to add a new custom service to my Drupal module"

**Your Response**:
1. Search `.agent/lessons-learned/` for "service", "dependency", "drupal"
2. Search `.agent/sops/` for "service", "development", "drupal"
3. Read found files
4. Present summary with:
   - Lessons about common service mistakes (e.g., static service access)
   - SOPs for creating services (if any)
   - System docs about existing services architecture
   - Key reminders (use DI, type declarations, etc.)

## Quick Reference Mode

If the user just types `/check-sops` without context:
- Ask what they're working on
- Offer a menu of common task types:
  - 🐛 Bug fix
  - ✨ New feature
  - ♻️ Refactoring/improvement
  - 🚀 Deployment
  - 🔍 Code review
  - 📦 Adding dependency
  - 🗄️ Database changes
  - Other (specify)

## Important Notes

- **Be concise**: Developers want quick references, not essays
- **Prioritize**: Show most relevant items first
- **Link**: Always provide file paths so they can read full details
- **Actionable**: Focus on practical, actionable information
- **Encourage**: Make it feel helpful, not burdensome
