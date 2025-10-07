# Custom Commands Guide
## Claude Code Custom Commands Reference

**Last Updated**: 2025-01-05

---

## 📁 Custom Command Structure

### Project Commands (Shared with Team)
```bash
.claude/
└── commands/
    ├── conversation-flow.md    # Our custom command
    ├── optimize.md             # Example: code optimization
    └── frontend/               # Namespaced commands
        └── component.md        # Creates /project:frontend:component
```

### User Commands (Personal)
```bash
~/.claude/
└── commands/
    ├── my-workflow.md
    └── shortcuts/
        └── quick-doc.md
```

---

## 🎯 Available Custom Commands

### `/conversation-flow`

**Purpose**: Generate or update conversation flow documentation

**Basic Usage**:
```bash
/conversation-flow
```

**With Options**:
```bash
# Concise style
/conversation-flow --style concise

# Technical focus
/conversation-flow --style technical

# Last 10 prompts only
/conversation-flow --limit 10

# Without quality ratings
/conversation-flow --no-quality

# Include recommendations
/conversation-flow --recommendations

# Update existing (append new only)
/conversation-flow --update

# Recreate from scratch
/conversation-flow --recreate
```

**Configuration**: `.claude/conversation-flow-config.yml`

**Output**: `CONVERSATION_FLOW.md` in project root

---

## ⚙️ Configuration System

### Configuration File Location

```bash
# Project-specific config (shared with team)
.claude/conversation-flow-config.yml

# User-specific config (personal preferences)
~/.claude/conversation-flow-config.yml
```

### Configuration Priority

1. Command-line arguments (highest priority)
2. Project config (`.claude/conversation-flow-config.yml`)
3. User config (`~/.claude/conversation-flow-config.yml`)
4. Default settings (lowest priority)

### Key Configuration Options

```yaml
# Summary style
style: detailed  # concise | detailed | technical

# Sections to include
sections:
  prompts: true
  responses: true
  findings: true
  quality_ratings: true
  decision_points: true
  overall_analysis: true
  recommendations: false

# Length controls
length:
  per_prompt_max_words: 200
  total_max_prompts: null
  include_minor_prompts: true

# Output formatting
output:
  include_timestamps: true
  include_token_counts: false
  include_examples: true
  table_format: markdown
```

---

## 🛠️ Creating Your Own Commands

### 1. Basic Command Structure

**File**: `.claude/commands/my-command.md`

```markdown
# My Custom Command

Brief description of what the command does.

## Task

I'll [action description] for $ARGUMENTS following [standards/practices].

## Process

I'll follow these steps:

1. Step 1 description
2. Step 2 description
3. Final step description

## Usage Examples

```bash
/my-command
/my-command --option value
```

## Expected Output

Description of what the command returns.
```

### 2. Using Arguments

Use `$ARGUMENTS` placeholder to accept parameters:

```markdown
# Analyze Performance

Analyze code performance for $ARGUMENTS and suggest optimizations.

## Task

I'll analyze the following files: $ARGUMENTS

## Process

1. Read each file in $ARGUMENTS
2. Identify performance bottlenecks
3. Suggest specific optimizations
```

**Usage**:
```bash
/analyze-performance src/app.py src/utils.py
```

### 3. Namespaced Commands

**File**: `.claude/commands/frontend/component.md`

**Creates**: `/project:frontend:component`

**Benefits**:
- Organize commands by category
- Avoid name conflicts
- Clear command purpose

---

## 📊 Command Best Practices

### 1. Clear Naming

✅ **Good**:
- `/conversation-flow`
- `/optimize-queries`
- `/security-audit`

❌ **Bad**:
- `/cf`
- `/opt`
- `/sec`

### 2. Single Responsibility

Each command should do **one thing well**:

✅ **Good**:
- `/generate-tests` - Only generates tests
- `/run-tests` - Only runs tests
- `/analyze-coverage` - Only analyzes coverage

❌ **Bad**:
- `/test-everything` - Generates, runs, and analyzes

### 3. Helpful Output

Include:
- ✅ What was done
- ✅ Where output was saved
- ✅ Next steps or recommendations
- ✅ Any warnings or issues

### 4. Configuration Support

For complex commands:
- ✅ Create a config file (`.claude/command-name-config.yml`)
- ✅ Support command-line overrides
- ✅ Provide sensible defaults
- ✅ Document all options

---

## 🎨 Styling Conventions

### Markdown Format

Use proper markdown formatting:

```markdown
# Command Name (H1 for title)

## Section (H2 for major sections)

### Subsection (H3 for details)

- Bullet points for lists
- `Code formatting` for commands/code
- **Bold** for emphasis
- *Italic* for notes
```

### Emoji Usage

Use emojis for quick visual scanning:

- ✅ Success / Good practice
- ❌ Error / Bad practice
- ⚠️ Warning / Needs attention
- 📁 File / Directory
- 🎯 Goal / Objective
- 🛠️ Tool / Action
- 📊 Analysis / Data
- 🔧 Configuration
- 💡 Tip / Recommendation

### Code Blocks

Always specify language:

````markdown
```bash
/command-name --option value
```

```yaml
key: value
```

```python
def example():
    pass
```
````

---

## 📚 Example Commands

### Code Quality Command

**File**: `.claude/commands/quality-check.md`

```markdown
# Code Quality Check

Run all code quality tools and generate a report.

## Task

I'll run linting, formatting checks, and type checking for $ARGUMENTS.

## Process

1. Run Black formatting check
2. Run flake8 linting
3. Run mypy type checking
4. Generate summary report

## Usage

```bash
/quality-check
/quality-check src/
/quality-check --fix
```

## Expected Output

Summary of all quality checks with pass/fail status.
```

### Documentation Generator

**File**: `.claude/commands/doc-gen.md`

```markdown
# Documentation Generator

Generate comprehensive documentation for $ARGUMENTS.

## Task

I'll analyze code and generate markdown documentation.

## Process

1. Read all files in $ARGUMENTS
2. Extract docstrings and type hints
3. Generate markdown documentation
4. Save to docs/ directory

## Usage

```bash
/doc-gen src/
/doc-gen src/api/ --format detailed
```
```

---

## 🔍 Testing Commands

### Manual Testing

```bash
# List all commands
/help

# Test your command
/your-command arg1 arg2

# Check output
ls -la  # Verify files created
cat output.md  # Verify content
```

### Validation Checklist

- [ ] Command appears in `/help`
- [ ] Command executes without errors
- [ ] Arguments are processed correctly
- [ ] Output is generated as expected
- [ ] Configuration is respected
- [ ] Documentation is clear

---

## 📦 Sharing Commands

### With Your Team (Project Commands)

1. Create command in `.claude/commands/`
2. Commit to git
3. Team members pull changes
4. Command available automatically

### With Community (User Commands)

1. Share command file on GitHub
2. Users download to `~/.claude/commands/`
3. Document in README

### Package as Template

Create a repository with:
```
my-claude-commands/
├── README.md
├── .claude/
│   └── commands/
│       ├── command1.md
│       └── command2.md
└── configs/
    ├── command1-config.yml
    └── command2-config.yml
```

---

## 🚀 Advanced Patterns

### Chained Commands

Command A generates input for Command B:

```bash
# Command A creates analysis.json
/analyze-codebase

# Command B uses analysis.json
/generate-improvements
```

### Conditional Logic

Use configuration to enable/disable features:

```yaml
# command-config.yml
features:
  include_tests: true
  include_docs: false
  include_examples: true
```

### Template Variables

Support placeholders in config:

```yaml
# config.yml
project:
  name: "{{PROJECT_NAME}}"
  owner: "{{GITHUB_USER}}"

# Command replaces at runtime
```

---

## 💡 Tips & Tricks

### 1. Use Descriptive Names

Good command names are self-documenting:
- `/conversation-flow` ✅
- `/cf` ❌

### 2. Provide Examples

Always include usage examples in command docs.

### 3. Version Your Commands

Track changes to commands:
```markdown
# Command Name

**Version**: 1.2.0
**Last Updated**: 2025-01-05

## Changelog

- v1.2.0: Added --limit option
- v1.1.0: Added configuration support
- v1.0.0: Initial version
```

### 4. Document Edge Cases

Note special behavior:
```markdown
## Notes

- Command requires git repository
- Large files may timeout
- Configuration file is optional
```

### 5. Error Handling

Specify what happens on errors:
```markdown
## Error Handling

- Missing file: Skip and continue
- Invalid config: Use defaults
- Network error: Retry 3 times
```

---

## 🔗 Resources

### Official Documentation
- [Claude Code Slash Commands](https://docs.claude.com/en/docs/claude-code/slash-commands)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

### Community Examples
- [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code)
- [Claude Command Suite](https://github.com/qdhenry/Claude-Command-Suite)
- [Claude Code Templates](https://github.com/davila7/claude-code-templates)

### Configuration Examples
- See `.claude/conversation-flow-config.yml` for full example
- Check community repos for more patterns

---

## 📝 Quick Reference

```bash
# Create command directory
mkdir -p .claude/commands

# Create a command
nano .claude/commands/my-command.md

# Test command
/help  # Verify it appears
/my-command  # Test execution

# Create config
nano .claude/my-command-config.yml

# Share with team
git add .claude/
git commit -m "Add custom command"
git push
```

---

**Happy Command Creating! 🚀**
