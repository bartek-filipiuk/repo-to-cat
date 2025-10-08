# Drupal 10 Code Review Checklist

**Date**: YYYY-MM-DD
**Reviewer**: [Your Name]
**Module/Feature**: [Name of module or feature being reviewed]
**Branch/PR**: [Branch name or PR number]

---

## 1. Dependency Injection
- [ ] No direct service access via `\Drupal::service()` in services
- [ ] All dependencies injected via constructor
- [ ] `create()` method properly implements `ContainerInterface`
- [ ] Services are properly defined in `*.services.yml`

**Issues found:**
```
[List any issues here, or write "None"]
```

---

## 2. Type Declarations
- [ ] All function parameters have type declarations
- [ ] All function return types are declared
- [ ] Constructor properties use typed properties (PHP 8+)
- [ ] Nullable types use `?` or union types where appropriate

**Issues found:**
```
[List any issues here, or write "None"]
```

---

## 3. Documentation
- [ ] All classes have complete docblocks
- [ ] All methods have complete docblocks
- [ ] Complex logic has inline comments
- [ ] `@param` and `@return` tags match actual type declarations
- [ ] `@throws` documented for methods that throw exceptions

**Issues found:**
```
[List any issues here, or write "None"]
```

---

## 4. Input Validation
- [ ] All user input is validated before use
- [ ] Form inputs use proper form validation
- [ ] Database inputs are sanitized
- [ ] Query parameters are validated
- [ ] No direct use of `$_GET`, `$_POST`, `$_REQUEST`

**Issues found:**
```
[List any issues here, or write "None"]
```

---

## 5. Translation Handling
- [ ] No global `t()` function in services or controllers
- [ ] Translation service (`TranslatableMarkup`) injected where needed
- [ ] All user-facing strings are translatable
- [ ] Context provided for ambiguous strings
- [ ] Plural forms handled correctly

**Issues found:**
```
[List any issues here, or write "None"]
```

---

## 6. Database Operations
- [ ] No direct SQL queries (use Query Builder API)
- [ ] Database service injected, not accessed statically
- [ ] Queries use placeholders for dynamic values
- [ ] Proper use of `->execute()` vs `->fetchAll()`
- [ ] Transactions used where appropriate

**Issues found:**
```
[List any issues here, or write "None"]
```

---

## 7. Code Structure
- [ ] `declare(strict_types=1);` at top of PHP files
- [ ] PHP 8.3+ features used where appropriate (readonly, etc.)
- [ ] No deprecated functions or methods used
- [ ] Proper namespace usage
- [ ] PSR-12 coding standards followed

**Issues found:**
```
[List any issues here, or write "None"]
```

---

## 8. Configuration Files
- [ ] YAML files properly structured and indented
- [ ] Schema defined for custom configuration
- [ ] Default configuration provided in `config/install/`
- [ ] Dependencies and required modules declared
- [ ] Permissions and routes properly defined

**Issues found:**
```
[List any issues here, or write "None"]
```

---

## 9. Security
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities (proper output escaping)
- [ ] CSRF protection in place for forms
- [ ] Proper access control checks
- [ ] Sensitive data not logged or exposed

**Issues found:**
```
[List any issues here, or write "None"]
```

---

## 10. Testing
- [ ] Unit tests written for new services/functions
- [ ] Tests use mocking for dependencies
- [ ] Edge cases covered in tests
- [ ] Tests pass locally

**Issues found:**
```
[List any issues here, or write "None"]
```

---

## Summary

**Total Issues Found**: [Number]

**Severity Breakdown**:
- Critical: [Number]
- High: [Number]
- Medium: [Number]
- Low: [Number]

**Recommendation**: [ ] Approve [ ] Request Changes [ ] Reject

**Overall Notes**:
```
[General observations, patterns, or recommendations]
```

---

## Follow-up Actions
- [ ] [Action item 1]
- [ ] [Action item 2]
- [ ] [Action item 3]

## Lessons Learned
[If any new mistakes were discovered, note them here to create lesson-learned documents later]

---
**Review completed**: YYYY-MM-DD
**Next review**: [If applicable]
