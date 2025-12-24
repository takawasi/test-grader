# test-grader

Grade AI-generated tests for quality before they break production.

AI-generated tests often pass but test nothing. Catch them early.

## Quick Start

```bash
# 1. Install
pip install test-grader

# 2. Grade
test-grader ./tests

# 3. CI gate
test-grader ./tests --min-score 70
```

## Features

- **Multi-language**: Python (pytest) + JavaScript (Jest)
- **Actionable**: Shows specific issues
- **CI-ready**: `--min-score` for quality gates
- **Fast**: Pure static analysis

## Output Example

```
Test Quality Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

test_user_login.py                   Score: 85/100 ✓
  ├─ Assertions: 4 per test
  ├─ Mocks: 1 per test
  └─ Issues: None

test_payment_flow.py                 Score: 45/100 ✗
  ├─ Assertions: 1 per test
  ├─ Mocks: 5 per test
  └─ Issues (3):
     - test_charge: No assertions found
     - test_refund: Too many mocks (5)
     - test_void: Test name not descriptive

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Score: 65/100
Files: 2 total, 1 passing, 1 failing
```

## Usage

```bash
# Grade tests in current directory
test-grader ./tests

# Grade single file
test-grader ./tests/test_user.py

# Set minimum passing score
test-grader ./tests --min-score 70

# JSON output
test-grader ./tests --format json

# Show all issues
test-grader ./tests --verbose
```

## What It Detects

| Issue | Impact |
|-------|--------|
| No assertions | Test does nothing |
| Trivial assertions | `assert True` always passes |
| Too many mocks | Testing mocks, not code |
| Short test body | Likely incomplete |
| Poor test names | Hard to understand failures |

## Scoring

| Score | Meaning |
|-------|---------|
| 80-100 | Good quality |
| 60-79 | Needs improvement |
| 0-59 | Likely useless |

## Supported Files

| Language | Patterns |
|----------|----------|
| Python | `test_*.py`, `*_test.py` |
| JavaScript | `*.test.js`, `*.spec.js`, `*.test.ts`, `*.spec.ts` |

## License

MIT
