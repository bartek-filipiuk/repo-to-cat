# LL-[TECH]-[NUMBER]: [Short Description of Mistake]

---
**ID**: LL-[TECH]-[NUMBER]
**Category**: [bug-fix|improvement|feature|deployment|performance|security]
**Technology**: [drupal|php|javascript|etc]
**Severity**: [critical|high|medium|low]
**Date Identified**: YYYY-MM-DD
**Frequency**: [how-often-this-occurs: first-time|occasional|frequent]
**Stage**: [development|testing|staging|production]

---

## The Mistake
[Clear, concise description of what went wrong]

### Context
**What were you trying to do?**
[Describe the original task or goal]

**What happened instead?**
[Describe the actual outcome]

### Example (Bad Practice)
```php
// Example of the mistake
class MyService {
  public function doSomething() {
    // ❌ WRONG: What you did that caused the problem
    $database = \Drupal::database();
  }
}
```

## Why It's a Problem
**Impact:**
- [Consequence 1 - e.g., breaks testability]
- [Consequence 2 - e.g., violates Drupal standards]
- [Consequence 3 - e.g., causes performance issues]

**Root Cause:**
[Why did this mistake happen? Lack of knowledge? Misunderstanding? Time pressure?]

## The Solution
[Explanation of the correct approach]

### Example (Best Practice)
```php
// Example of the correct implementation
class MyService {
  public function __construct(
    private readonly Connection $database,
  ) {}

  public static function create(ContainerInterface $container): static {
    return new static(
      $container->get('database'),
    );
  }

  public function doSomething(): void {
    // ✅ CORRECT: Use injected dependency
    $this->database->select('table', 't');
  }
}
```

## How to Detect This Issue
**Manual detection:**
- [How to spot this in code review]
- [Warning signs to look for]

**Automated detection:**
- [Linter rules that can catch this]
- [Tests that would fail]
- [Tools that can help: e.g., phpstan, rector]

## Prevention Strategies
To avoid this mistake in the future:
- [ ] [Add/update coding standard or checklist]
- [ ] [Configure linter or static analysis tool]
- [ ] [Add to code review checklist]
- [ ] [Create/update related SOP]
- [ ] [Add automated test]

## References
- [Related SOPs](../sops/)
- [Drupal documentation link]
- [Stack Overflow or other helpful resources]

## Related Lessons
- [LL-XXX-YYY: Similar issue](./LL-XXX-YYY.md)

## Follow-up Actions Taken
- [ ] Updated [SOP-XXX]: [description]
- [ ] Added linter rule: [rule name]
- [ ] Shared with team on: [date]
- [ ] Added to onboarding materials

---
**Status**: [captured|reviewed|implemented|archived]
**Tags**: `#drupal` `#[specific-topic]` `#[category]`
