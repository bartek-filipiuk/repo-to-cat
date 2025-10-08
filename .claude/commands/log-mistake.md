---
description: Capture a mistake from current conversation
---

Analyze the recent conversation to identify any mistakes, errors, or issues that occurred. Then create a concise lesson-learned document.

## Your Task

1. **Review the conversation** - Look for:
   - Errors that occurred
   - Wrong approaches that were corrected
   - Anti-patterns that were identified
   - Things that didn't work as expected

2. **Extract the key mistake** - Identify the main issue

3. **Create concise lesson-learned doc**:
   - Determine the next ID number (check `.agent/lessons-learned/`)
   - Use format: `LL-[TECH]-[NUM]-[short-name].md`
   - Keep it SHORT and actionable

4. **Document structure** (keep minimal):
   ```markdown
   # LL-[TECH]-[NUM]: [Short Title]

   **Tech**: [technology] | **Severity**: [high/medium/low] | **Date**: YYYY-MM-DD

   ## The Mistake
   [What went wrong - 1-2 sentences]

   ## Why It's Wrong
   - [Key reason 1]
   - [Key reason 2]

   ## The Fix
   [What to do instead - 1-2 sentences]

   ```[language]
   // Code example if applicable
   ```

   ## How to Detect
   - [How to spot this]

   ## Prevention
   - [How to avoid it]
   ```

5. **Update `.agent/README.md`** - Add to the lessons learned table

## Keep It Short

- Focus on the ONE main mistake
- 2-3 sentences max per section
- Include code only if essential
- Make it scannable

If no clear mistake is found in the conversation, tell the user and ask them to describe what went wrong.
