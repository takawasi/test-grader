"""Output formatters for test-grader."""

from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .scorer import TestScore


def print_report(scores: List[TestScore], console: Console, verbose: bool = False):
    """Print quality report."""
    console.print()
    console.print("[bold]Test Quality Report[/bold]")
    console.print("━" * 50)
    console.print()

    total_score = 0
    passing = 0
    failing = 0

    for score in scores:
        _print_file_score(score, console, verbose)
        total_score += score.score
        if score.score >= 70:
            passing += 1
        else:
            failing += 1

    # Summary
    avg_score = total_score / len(scores) if scores else 0
    console.print("━" * 50)
    style = "green" if avg_score >= 70 else "red"
    console.print(f"[bold]Overall Score:[/bold] [{style}]{int(avg_score)}/100[/{style}]")
    console.print(f"Files: {len(scores)} total, [green]{passing} passing[/green], [red]{failing} failing[/red]")


def _print_file_score(score: TestScore, console: Console, verbose: bool):
    """Print score for a single file."""
    # Score indicator
    if score.score >= 70:
        indicator = "[green]✓[/green]"
        style = "green"
    else:
        indicator = "[red]✗[/red]"
        style = "red"

    # File header
    path_short = score.path.split('/')[-1] if '/' in score.path else score.path
    console.print(f"[bold]{path_short:40}[/bold] Score: [{style}]{score.score}/100[/{style}] {indicator}")

    # Details
    console.print(f"  ├─ Assertions: {score.avg_assertions} per test", style="dim")
    console.print(f"  ├─ Mocks: {score.mock_ratio} per test", style="dim")

    if score.issues:
        console.print(f"  └─ [yellow]Issues ({len(score.issues)}):[/yellow]")
        issues_to_show = score.issues if verbose else score.issues[:3]
        for issue in issues_to_show:
            console.print(f"     - {issue}", style="dim")
        if not verbose and len(score.issues) > 3:
            console.print(f"     ... and {len(score.issues) - 3} more", style="dim")
    else:
        console.print("  └─ Issues: None", style="dim green")

    console.print()


def to_json(scores: List[TestScore]) -> str:
    """Convert scores to JSON."""
    import json
    output = []
    for s in scores:
        output.append({
            'path': s.path,
            'score': s.score,
            'tests_count': s.tests_count,
            'avg_assertions': s.avg_assertions,
            'mock_ratio': s.mock_ratio,
            'issues': s.issues,
        })
    return json.dumps(output, indent=2)
