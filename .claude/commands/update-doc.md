---
description: Initialize or update the .agent documentation system
---

You are helping maintain the .agent documentation system for this Drupal project.

## Documentation Structure

The `.agent` folder contains:
- **tasks/** - Implementation plans and Product Requirement Documents (PRDs)
- **system/** - Project architecture, database schema, API endpoints, critical code
- **sops/** - Standard Operating Procedures for common tasks
- **lessons-learned/** - Captured mistakes and their solutions
- **templates/** - Templates for creating new documentation
- **README.md** - Index of all documentation (the entry point)

## When Initializing (first time)

If `.agent/README.md` does NOT exist yet:

1. **Create project architecture document**
   - Analyze the current project structure
   - Document the directory layout, key modules, and technologies used
   - Save as `.agent/system/project-architecture.md`
   - Include: directory structure, main components, tech stack, configuration locations

2. **Create README.md index**
   - Create `.agent/README.md` with:
     - Overview of the documentation system
     - List of all existing documents organized by folder
     - Quick navigation links
     - Instructions on how to use the documentation

3. **Provide summary**
   - Tell the user what was created
   - Explain the folder structure
   - Suggest next steps (like creating initial SOPs)

## When Updating (after initialization)

If `.agent/README.md` EXISTS:

1. **Update based on context**
   - If given specific instructions (e.g., "generate SOP for X"), create that document
   - If asked to update after implementing a feature, document the changes in:
     - Update `system/project-architecture.md` if structure changed
     - Create/update relevant SOP if a new process was followed
     - Save implementation plan in `tasks/` if it was a significant feature

2. **Update README.md**
   - Add new documents to the index
   - Update the "Last Updated" date
   - Keep the navigation structure clear and organized

3. **Follow naming conventions**
   - SOPs: `SOP-[CATEGORY]-[NUMBER]-[short-description].md`
   - Lessons: `LL-[TECH]-[NUMBER]-[short-description].md`
   - Tasks: `TASK-[YYYY-MM-DD]-[feature-name].md`
   - System docs: descriptive names like `database-schema.md`, `api-endpoints.md`

## Specific Rules

1. **Always read `.agent/README.md` first** before creating new docs to avoid duplicates
2. **Keep documents focused** - one topic per document
3. **Cross-reference** - link related documents to each other
4. **Use templates** - when creating SOPs or lessons learned, use the templates in `.agent/templates/`
5. **Version control** - include "Last Updated" dates and version numbers where appropriate
6. **Be concise but complete** - developers need actionable information, not essays

## Your Task Now

Based on the user's request, either:
- Initialize the documentation system (if first time)
- Update documentation with new information (if already initialized)

Make sure to update the README.md index after creating or modifying any documents.
