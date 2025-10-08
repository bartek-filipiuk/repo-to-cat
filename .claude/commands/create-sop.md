---
description: Create a new Standard Operating Procedure (SOP) from template
---

You are helping create a new Standard Operating Procedure (SOP) to document a process or best practice.

## Your Task

Guide the user through creating a well-structured SOP document that will help prevent mistakes and standardize processes.

## Process

### 1. Gather Requirements

Ask the user:

**Basic Information:**
- What process or procedure do you want to document?
- What category does this fall into?
  - `DEV` - Development (code review, testing, coding standards)
  - `DEPLOY` - Deployment (CI/CD, releases, rollbacks)
  - `OPS` - Operations (monitoring, maintenance, backups)
  - `SEC` - Security (authentication, vulnerability management)
  - `DATA` - Database operations
  - `TEST` - Testing procedures
  - Other (specify)

- What priority level is this? (critical, high, medium, low)

**Purpose:**
- Why is this SOP needed?
- What problem does it solve or what goal does it achieve?
- Who will use this SOP? (developers, devops, all engineering, etc.)

**Scope:**
- When should someone use this SOP?
- When should they NOT use it?

### 2. Determine SOP Number

1. Look at existing SOPs in `.agent/sops/`
2. Find the highest number in the chosen category
3. Increment by 1
4. Format: `SOP-[CATEGORY]-[NUMBER]-[short-description].md`

**Examples:**
- `SOP-DEV-001-code-review-process.md`
- `SOP-DEPLOY-001-production-deployment.md`
- `SOP-SEC-001-access-management.md`

### 3. Create the SOP

1. **Read the template**: Load `.agent/templates/sop-template.md`

2. **Create the new file** with proper naming

3. **Fill in the sections** by asking the user:

   **Header:**
   - ID, Category, Technology, Priority, Owner

   **Purpose:**
   - Clear 1-2 sentence explanation of why this SOP exists

   **Scope:**
   - When to use it
   - When NOT to use it

   **Prerequisites:**
   - What tools, access, or knowledge are needed?

   **Procedure:**
   - Step-by-step instructions
   - Each step should be:
     - Clear and actionable (start with action verb)
     - Include code examples or commands where applicable
     - State expected outcomes

   **Validation:**
   - How to verify the procedure was successful

   **Troubleshooting:**
   - Common problems and their solutions

   **Related Resources:**
   - Links to related SOPs, docs, or external resources

### 4. Enhance the SOP

**Make it actionable:**
- Include copy-paste commands where possible
- Add code examples for technical procedures
- Include expected outputs so users know what success looks like

**Make it discoverable:**
- Add relevant tags at the bottom
- Link to related SOPs and lessons learned
- Add proper metadata in the header

**Make it maintainable:**
- Add version number and last updated date
- Specify owner/maintainer
- Include revision history table

### 5. Update Documentation System

1. **Update `.agent/README.md`**:
   - Add the new SOP to the index
   - Keep organized by category
   - Update the "Last Updated" date

2. **Cross-reference**:
   - If this SOP relates to existing lessons learned, add references
   - If there are related SOPs, link them bidirectionally

### 6. Provide Summary

Give the user:
- Confirmation of what was created
- Path to the new SOP
- Suggestions for:
  - Testing the SOP (have someone unfamiliar follow it)
  - Related SOPs that might need updates
  - Where to reference this SOP (code review checklist, CI/CD, etc.)

## SOP Quality Checklist

Before finalizing, verify:
- [ ] Clear, descriptive title
- [ ] Purpose is obvious (why does this exist?)
- [ ] Prerequisites are listed
- [ ] Steps are numbered and actionable
- [ ] Code examples or commands included (if applicable)
- [ ] Expected outcomes stated
- [ ] Troubleshooting section has common issues
- [ ] Related resources linked
- [ ] Proper metadata in header
- [ ] Added to README.md index
- [ ] Tags added for searchability

## Examples of Good SOPs

**SOP-DEV-001: Code Review Process**
- Clear steps for reviewer and reviewee
- Checklist of what to look for
- How to handle disagreements
- Links to coding standards

**SOP-DEPLOY-001: Production Deployment**
- Pre-deployment checklist
- Step-by-step deployment commands
- Verification steps
- Rollback procedure
- Emergency contacts

**SOP-DATA-001: Database Schema Changes**
- When to create migration
- How to write reversible migrations
- Testing procedure
- Deployment sequence
- Backup requirements

## Tone and Style

- **Imperative voice**: "Run the command" not "You should run the command"
- **Concise**: Short sentences, clear language
- **Complete**: Don't skip steps assuming knowledge
- **Tested**: Verify the steps actually work
- **Practical**: Focus on real-world execution

## After Creation

Encourage the user to:
- Test the SOP by following it themselves
- Have a colleague review it
- Update it based on feedback
- Reference it in relevant places (README, PR templates, CI/CD, etc.)
