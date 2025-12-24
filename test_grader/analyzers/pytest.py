"""pytest analyzer - Extract metrics from Python test files."""

import ast
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class TestMetrics:
    """Metrics for a single test function."""
    name: str
    assertions: int
    mocks: int
    lines: int
    issues: List[str]


@dataclass
class FileMetrics:
    """Metrics for a test file."""
    path: str
    tests: List[TestMetrics]
    total_assertions: int
    total_mocks: int


def analyze_pytest(path: Path) -> FileMetrics:
    """Analyze a pytest file and extract metrics.

    Metrics extracted:
    - assertion count per test
    - mock/patch usage count
    - test function count
    - issues (empty tests, trivial assertions, etc.)
    """
    content = path.read_text()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return FileMetrics(str(path), [], 0, 0)

    tests = []
    total_assertions = 0
    total_mocks = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            metrics = _analyze_test_function(node)
            tests.append(metrics)
            total_assertions += metrics.assertions
            total_mocks += metrics.mocks

    return FileMetrics(
        path=str(path),
        tests=tests,
        total_assertions=total_assertions,
        total_mocks=total_mocks,
    )


def _analyze_test_function(func: ast.FunctionDef) -> TestMetrics:
    """Analyze a single test function."""
    assertions = 0
    mocks = 0
    issues = []

    for node in ast.walk(func):
        # Count assertions
        if isinstance(node, ast.Assert):
            assertions += 1
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                # pytest-style assertions: assert_*, assertEqual, etc.
                if node.func.attr.startswith('assert'):
                    assertions += 1
                # Mock detection
                elif node.func.attr in ('patch', 'Mock', 'MagicMock', 'mock_open'):
                    mocks += 1
            elif isinstance(node.func, ast.Name):
                if node.func.id in ('patch', 'Mock', 'MagicMock'):
                    mocks += 1

    # Detect issues
    if assertions == 0:
        issues.append("No assertions found")
    elif assertions == 1:
        # Check for trivial assertion
        for node in ast.walk(func):
            if isinstance(node, ast.Assert):
                if _is_trivial_assertion(node):
                    issues.append("Trivial assertion (always true)")

    if mocks > 3:
        issues.append(f"Too many mocks ({mocks})")

    if len(func.body) <= 2:
        issues.append("Test body too short")

    # Check test name quality
    if func.name == 'test_':
        issues.append("Empty test name")
    elif len(func.name) < 10:
        issues.append("Test name not descriptive")

    return TestMetrics(
        name=func.name,
        assertions=assertions,
        mocks=mocks,
        lines=func.end_lineno - func.lineno + 1 if func.end_lineno else 1,
        issues=issues,
    )


def _is_trivial_assertion(node: ast.Assert) -> bool:
    """Check if assertion is trivial (always true)."""
    test = node.test

    # assert True
    if isinstance(test, ast.Constant) and test.value is True:
        return True

    # assert 1 == 1
    if isinstance(test, ast.Compare):
        if len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq):
            left = test.left
            right = test.comparators[0]
            if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
                if left.value == right.value:
                    return True

    return False
