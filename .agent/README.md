# .agent Documentation System

**Last Updated**: 2025-10-08
**Version**: 1.0
**Status**: Active

---

## 📚 Overview

This directory contains the knowledge base and documentation system for our Drupal development workflow. It helps us avoid mistakes, standardize processes, and build institutional knowledge over time.

### Purpose
- **Prevent mistakes**: Learn from past errors and avoid repeating them
- **Standardize processes**: Follow consistent procedures across the team
- **Build knowledge**: Create a growing repository of lessons and best practices
- **Improve quality**: Catch issues early through checklists and guidelines

### How to Use This System

**Before starting any task:**
```bash
/check-sops
```
This will show you relevant SOPs and lessons learned for your task.

**When you make a mistake:**
```bash
/log-mistake
```
Document what went wrong so the team can learn from it.

**To create a new SOP:**
```bash
/create-sop
```
Follow the guided process to document a new procedure.

**To update documentation:**
```bash
/update-doc
```
Update project architecture or add new documentation.

---

## 📂 Directory Structure

```
.agent/
├── README.md                    # This file - start here!
├── templates/                   # Templates for creating new docs
│   ├── sop-template.md
│   ├── lesson-learned-template.md
│   └── drupal-code-review-checklist.md
├── sops/                        # Standard Operating Procedures
│   ├── SOP-DEV-001-dependency-injection.md
│   ├── SOP-DEV-002-type-declarations.md
│   └── SOP-DEV-003-code-review-drupal.md
├── lessons-learned/             # Documented mistakes and solutions
│   ├── LL-DRUPAL-001-static-service-access.md
│   └── LL-PHP-001-missing-type-declarations.md
├── tasks/                       # Implementation plans and PRDs
│   └── (implementation plans saved here)
└── system/                      # Project architecture docs
    └── (system documentation saved here)
```

---

## 📋 Standard Operating Procedures (SOPs)

SOPs provide step-by-step guidance for common tasks and processes.

### Development

| ID | Title | Priority | Description |
|----|-------|----------|-------------|
| [SOP-DEV-001](sops/SOP-DEV-001-dependency-injection.md) | Dependency Injection | High | How to properly inject services instead of using static calls |
| [SOP-DEV-002](sops/SOP-DEV-002-type-declarations.md) | Type Declarations | High | Guide to using PHP type declarations for all parameters and returns |
| [SOP-DEV-003](sops/SOP-DEV-003-code-review-drupal.md) | Code Review Process | Critical | Complete code review checklist and process for Drupal 10 |

### Quick Reference: When to Use Which SOP

- **Creating a new service?** → Read SOP-DEV-001 (Dependency Injection)
- **Writing any PHP code?** → Read SOP-DEV-002 (Type Declarations)
- **Reviewing code?** → Use SOP-DEV-003 (Code Review Process)

---

## 🚨 Lessons Learned

Captured mistakes and anti-patterns to avoid. These are real issues we've encountered.

### Drupal-Specific

| ID | Title | Severity | Description |
|----|-------|----------|-------------|
| [LL-DRUPAL-001](lessons-learned/LL-DRUPAL-001-static-service-access.md) | Static Service Access | High | Using `\Drupal::service()` instead of dependency injection |

### PHP-Specific

| ID | Title | Severity | Description |
|----|-------|----------|-------------|
| [LL-PHP-001](lessons-learned/LL-PHP-001-missing-type-declarations.md) | Missing Type Declarations | Medium | Writing functions without parameter and return types |

### By Category

**Development Issues:**
- LL-DRUPAL-001: Static Service Access
- LL-PHP-001: Missing Type Declarations

**To be added:**
- Input validation issues
- Translation handling mistakes
- Database operation anti-patterns
- Configuration file errors

---

## 📝 Templates

Use these templates when creating new documentation:

| Template | Purpose | Command |
|----------|---------|---------|
| [sop-template.md](templates/sop-template.md) | Create new SOPs | `/create-sop` |
| [lesson-learned-template.md](templates/lesson-learned-template.md) | Document mistakes | `/log-mistake` |
| [drupal-code-review-checklist.md](templates/drupal-code-review-checklist.md) | Code review form | Copy for each review |

---

## 🎯 Quick Start Guide

### For New Team Members

1. **Read this README** - You're doing it now! ✓
2. **Review key SOPs**:
   - Start with SOP-DEV-003 (Code Review Process)
   - Read SOP-DEV-001 (Dependency Injection)
   - Read SOP-DEV-002 (Type Declarations)
3. **Browse lessons learned** - See what mistakes to avoid
4. **Set up tools**: Configure phpstan, phpcs for automated checks

### For Existing Team Members

**Before any task:**
1. Run `/check-sops` to see relevant documentation
2. Review applicable SOPs and lessons learned
3. Follow the procedures outlined

**After completing a task:**
1. If you discovered a new pattern, run `/create-sop`
2. If you made a mistake, run `/log-mistake`
3. If it was a significant feature, run `/update-doc`

**During code review:**
1. Use the [Drupal Code Review Checklist](templates/drupal-code-review-checklist.md)
2. Check lessons learned for known anti-patterns
3. Reference SOPs in your review comments

---

## 🔍 Finding Information

### Search by Technology
```bash
# Find Drupal-specific docs
grep -r "drupal" .agent/ --include="*.md"

# Find PHP-specific docs
grep -r "php" .agent/ --include="*.md"
```

### Search by Topic
```bash
# Find dependency injection docs
grep -r "dependency injection" .agent/ --include="*.md"

# Find type-related docs
grep -r "type declaration" .agent/ --include="*.md"
```

### Using the Commands
```bash
/check-sops          # Show relevant SOPs for your current task
/log-mistake         # Document a mistake you made
/create-sop          # Create a new standard procedure
/update-doc          # Update system documentation
```

---

## 📊 Documentation Statistics

**Total Documents**: 8
- SOPs: 3
- Lessons Learned: 2
- Templates: 3
- System Docs: 0 (to be added)

**Coverage by Category**:
- Development: ✅ Well covered (3 SOPs, 2 lessons)
- Deployment: ⚠️ Not yet documented
- Operations: ⚠️ Not yet documented
- Security: ⚠️ Not yet documented

**Most Recent Updates**:
- 2025-10-08: Initial system setup
- 2025-10-08: Added core development SOPs
- 2025-10-08: Added first lessons learned

---

## 🔄 Maintenance

### Document Review Schedule
- **Critical SOPs**: Review quarterly
- **High priority SOPs**: Review semi-annually
- **Medium/Low priority**: Review annually
- **Lessons learned**: Review when similar issues occur

### Adding New Documentation

1. **New SOP**: Use `/create-sop` command or copy template
2. **New lesson**: Use `/log-mistake` command or copy template
3. **Update this README**: Add entry to appropriate section
4. **Cross-reference**: Link related documents

### Deprecating Documentation

When an SOP becomes outdated:
1. Add deprecation notice at top of document
2. Link to replacement document (if any)
3. Update status to "deprecated"
4. Move to archive folder after 3 months

---

## 🎓 Philosophy

This documentation system follows these principles:

1. **Blameless learning**: Focus on process improvement, not individual fault
2. **Actionable content**: Provide practical, copy-paste solutions
3. **Living documents**: Continuously update based on experience
4. **Searchable and organized**: Easy to find what you need
5. **Team-driven**: Everyone contributes to shared knowledge

---

## 🤝 Contributing

Everyone on the team should contribute to this knowledge base!

**How to contribute:**
- Document mistakes you make (use `/log-mistake`)
- Create SOPs for repeated tasks (use `/create-sop`)
- Update existing docs when processes change
- Add examples and code snippets
- Improve clarity of existing documentation
- Review and provide feedback on new docs

**Contribution Guidelines:**
- Use the provided templates
- Follow naming conventions (SOP-XXX-NNN, LL-XXX-NNN)
- Include code examples where applicable
- Link to related documents
- Keep language clear and concise
- Test procedures before documenting

---

## 📞 Getting Help

**Questions about the SOP system?**
- Ask in team chat
- Review this README
- Check individual SOP documentation

**Found an error in documentation?**
- Update it directly (it's a living system!)
- Or note it and ask for help

**Need to create new documentation type?**
- Discuss with team lead
- Create a template
- Document the new type in this README

---

## 🚀 Next Steps

**Immediate priorities:**
1. Use the system consistently on every task
2. Document mistakes as they happen (don't wait!)
3. Reference SOPs in code reviews
4. Add system architecture documentation

**Future enhancements:**
- Add deployment SOPs
- Add security procedures
- Add database operation guides
- Add more lessons learned
- Integrate with CI/CD for automated checks
- Add metrics tracking (how often docs are used)

---

**Remember**: This system only works if we use it! Make it a habit to:
- Check SOPs before starting tasks
- Log mistakes when they happen
- Reference docs in reviews
- Keep documentation updated

The goal is continuous improvement and shared learning. Every mistake is an opportunity to make the team better.
