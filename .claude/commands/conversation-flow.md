# Generate Conversation Flow Documentation

Analyze the current conversation and generate a concise conversation flow document.

## Task

I'll analyze the entire conversation and create a **focused, concise** document with:

1. **Your Original Prompts** - Full text (quoted)
2. **Actions** - What I did (brief, no code snippets)
3. **Result** - ✅ Good / ⚠️ Issues / ❌ Failed
4. **Key Points** - Important decisions only
5. **Summary** - Overall assessment (3-5 lines max)

## Output Format

**Default**: Concise, no fluff, straight to the point.

Each prompt gets:
- **#N**: Prompt number
- **Your Prompt**: Full original prompt text (quoted)
- **Did**: Brief action taken (NO code, NO long explanations)
- **Result**: ✅ Good / ⚠️ Partial / ❌ Failed
- **Notes**: Only if critical decision made

**Example**:
```
### #3
**Your Prompt**: "ok now prepare a agent sdk simple documentation with this knowledge what you have now, do not compare with other agents or do not put any billings etc. Just how claude agend sdk works, how it can be used, with examples"
**Did**: Created comprehensive SDK guide with examples and best practices
**Result**: ✅ Good - Complete documentation file created
**Notes**: Focus on practical usage only, no framework comparisons
```

## Configuration (Optional)

Create `.claude/conversation-flow-config.yml`:

```yaml
# Keep it simple
length:
  max_prompts: null           # Limit analyzed (null = all)
  skip_minor_prompts: true    # Skip "ok", "yes", etc.

output:
  filename: "CONVERSATION_FLOW.md"  # Output file name
```

## Process

1. Scan conversation from start
2. Extract FULL original prompts (quoted text, not summaries)
3. Summarize action taken per prompt (1-2 lines max)
4. Rate result (✅/⚠️/❌)
5. Note only critical decisions
6. Write to file specified in $ARGUMENTS or config

## Usage

```bash
# Default output (CONVERSATION_FLOW.md)
/conversation-flow

# Custom output name
/conversation-flow --output PR_DOCS_SESSION.md

# Different conversation session
/conversation-flow --output AUTH_FEATURE.md

# Limit to recent prompts
/conversation-flow --limit 10 --output RECENT.md
```

## Arguments

- `--output FILENAME`: Save to specific file (required for multiple sessions)
- `--limit N`: Analyze only last N prompts
- `--skip-minor`: Skip small prompts like "ok", "yes"

## Notes

- **NO code snippets** in output
- **NO long descriptions** - just facts
- **NO examples** unless critical
- Focus on: What was asked → What was done → Result
- Overall summary: 3-5 lines max

I'll keep it concise and focused on key information only.
