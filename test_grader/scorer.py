"""Test quality scorer."""

from typing import List
from dataclasses import dataclass


@dataclass
class TestScore:
    """Score for a single test file."""
    path: str
    score: int
    tests_count: int
    avg_assertions: float
    mock_ratio: float
    issues: List[str]


def score_file(path: str, tests: List, total_assertions: int, total_mocks: int) -> TestScore:
    """Calculate quality score for a test file.

    Scoring criteria (subject to inductive refinement):
    - Base score: 50
    - Assertions per test: +10 per assertion (up to +30)
    - Mock ratio: -5 per mock above 2 (per test avg)
    - Issues: -10 per issue
    - Test count: +5 if > 3 tests

    Score capped at 0-100.
    """
    if not tests:
        return TestScore(path, 0, 0, 0, 0, ["No tests found"])

    tests_count = len(tests)
    avg_assertions = total_assertions / tests_count if tests_count else 0
    mock_ratio = total_mocks / tests_count if tests_count else 0

    # Collect all issues
    all_issues = []
    for test in tests:
        for issue in test.issues:
            all_issues.append(f"{test.name}: {issue}")

    # Calculate score
    score = 50

    # Assertions bonus (max +30)
    assertions_bonus = min(avg_assertions * 10, 30)
    score += assertions_bonus

    # Mock penalty
    if mock_ratio > 2:
        score -= (mock_ratio - 2) * 5

    # Issues penalty
    score -= len(all_issues) * 5

    # Test count bonus
    if tests_count >= 3:
        score += 5

    # Clamp
    score = max(0, min(100, int(score)))

    return TestScore(
        path=path,
        score=score,
        tests_count=tests_count,
        avg_assertions=round(avg_assertions, 1),
        mock_ratio=round(mock_ratio, 1),
        issues=all_issues,
    )
