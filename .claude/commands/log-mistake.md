---
description: Capture a mistake or lesson learned for future reference
---

You are helping capture a mistake or lesson learned to prevent it from happening again.

## Your Task

Guide the user through documenting a mistake they made, using a **blameless, learning-focused approach**.

## Process

### 1. Gather Information

Ask the user these questions (adapt based on context):

**Basic Information:**
- What were you trying to do? (The original goal/task)
- What actually happened? (The mistake or unexpected outcome)
- What category does this fall into? (bug-fix, improvement, feature, deployment, performance, security)
- What technology is involved? (drupal, php, javascript, database, etc.)
- What stage were you in? (development, testing, staging, production)
- How severe was the impact? (critical, high, medium, low)

**Understanding the Mistake:**
- Can you show me the code or describe what you did wrong?
- Why is this problematic? (What are the consequences?)
- What caused this mistake? (Lack of knowledge? Misunderstanding? Time pressure? Unclear requirements?)

**The Solution:**
- How did you fix it or what should have been done instead?
- Can you show me the correct approach?

**Prevention:**
- How can we detect this issue in the future? (Manual checks? Automated tools?)
- What can we do to prevent this? (Update checklist? Add linter rule? Create/update SOP?)

### 2. Create the Lesson Learned Document

1. **Read the template**: Check `.agent/templates/lesson-learned-template.md`

2. **Determine the next ID number**:
   - Look at existing lessons in `.agent/lessons-learned/`
   - Find the highest number for the technology category
   - Increment by 1

3. **Create the document**:
   - Use filename format: `LL-[TECH]-[NUMBER]-[short-description].md`
   - Examples:
     - `LL-DRUPAL-001-static-service-access.md`
     - `LL-PHP-001-missing-type-declarations.md`
     - `LL-DATABASE-001-sql-injection-vulnerability.md`

4. **Fill in all sections**:
   - Include the actual code examples (before/after)
   - Be specific about the impact and root cause
   - Provide actionable prevention strategies
   - Link to related SOPs or documentation

### 3. Update Related Documentation

1. **Update `.agent/README.md`**:
   - Add the new lesson learned to the index
   - Keep it organized by category or date

2. **Consider creating/updating an SOP**:
   - If this mistake reveals a gap in procedures, suggest creating an SOP
   - If an existing SOP should be updated, note that

3. **Add to prevention systems** (if applicable):
   - Suggest adding to code review checklist
   - Recommend linter rules or static analysis configs
   - Propose automated tests

### 4. Provide Summary

Give the user:
- Confirmation of what was documented
- Path to the created file
- Suggestions for follow-up actions (SOPs to create/update, tools to configure, etc.)
- Encouragement - mistakes are learning opportunities!

## Tone and Approach

**IMPORTANT**: Use a **blameless, positive, learning-focused tone**:
- ✅ "This is a common mistake - let's capture how to avoid it"
- ✅ "Great catch! Documenting this will help prevent it in the future"
- ✅ "This will be valuable for the team to learn from"
- ❌ "You shouldn't have done that"
- ❌ "This was a bad practice"
- ❌ Any language that implies blame or judgment

## Example Interaction

```
User: I just realized I used \Drupal::service() in a service class instead of dependency injection