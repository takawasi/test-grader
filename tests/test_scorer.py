"""Tests for scorer."""

from test_grader.scorer import score_file


class MockTest:
    """Mock test metrics."""
    def __init__(self, name, assertions, mocks, issues=None):
        self.name = name
        self.assertions = assertions
        self.mocks = mocks
        self.lines = 10
        self.issues = issues or []


def test_score_good_tests():
    """Score file with good tests."""
    tests = [
        MockTest("test_one", 3, 0),
        MockTest("test_two", 4, 1),
        MockTest("test_three", 3, 0),
    ]
    score = score_file("test.py", tests, 10, 1)

    assert score.score >= 70
    assert score.tests_count == 3
    assert len(score.issues) == 0


def test_score_bad_tests():
    """Score file with bad tests."""
    tests = [
        MockTest("test_", 0, 5, ["No assertions found", "Too many mocks (5)"]),
    ]
    score = score_file("test.py", tests, 0, 5)

    assert score.score < 50
    assert len(score.issues) >= 2


def test_score_empty():
    """Score empty file."""
    score = score_file("test.py", [], 0, 0)

    assert score.score == 0
    assert "No tests found" in score.issues
