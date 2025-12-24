"""Jest analyzer - Extract metrics from JavaScript test files."""

import re
from pathlib import Path
from typing import List
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


def analyze_jest(path: Path) -> FileMetrics:
    """Analyze a Jest test file and extract metrics.

    Uses regex-based analysis (no JS parser dependency).
    """
    content = path.read_text()
    tests = []
    total_assertions = 0
    total_mocks = 0

    # Find test blocks: test('name', ...) or it('name', ...)
    test_pattern = r'(?:test|it)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]'
    test_matches = list(re.finditer(test_pattern, content))

    for i, match in enumerate(test_matches):
        start = match.start()
        # Find end of test block (approximate by next test or EOF)
        end = test_matches[i + 1].start() if i + 1 < len(test_matches) else len(content)
        test_body = content[start:end]

        metrics = _analyze_test_block(match.group(1), test_body)
        tests.append(metrics)
        total_assertions += metrics.assertions
        total_mocks += metrics.mocks

    return FileMetrics(
        path=str(path),
        tests=tests,
        total_assertions=total_assertions,
        total_mocks=total_mocks,
    )


def _analyze_test_block(name: str, body: str) -> TestMetrics:
    """Analyze a single test block."""
    issues = []

    # Count assertions: expect(...)
    assertions = len(re.findall(r'expect\s*\(', body))

    # Count mocks: jest.fn(), jest.mock(), jest.spyOn()
    mocks = len(re.findall(r'jest\.(fn|mock|spyOn)\s*\(', body))

    # Count lines
    lines = body.count('\n') + 1

    # Detect issues
    if assertions == 0:
        issues.append("No assertions found")

    # Check for trivial assertions
    if re.search(r'expect\s*\(\s*true\s*\)\s*\.toBe\s*\(\s*true\s*\)', body):
        issues.append("Trivial assertion (expect(true).toBe(true))")

    if mocks > 3:
        issues.append(f"Too many mocks ({mocks})")

    if lines < 3:
        issues.append("Test body too short")

    if len(name) < 5:
        issues.append("Test name not descriptive")

    return TestMetrics(
        name=name,
        assertions=assertions,
        mocks=mocks,
        lines=lines,
        issues=issues,
    )
