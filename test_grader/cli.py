"""CLI interface for test-grader."""

import sys
import click
from pathlib import Path
from rich.console import Console

from .analyzers.pytest import analyze_pytest
from .analyzers.jest import analyze_jest
from .scorer import score_file
from .output import print_report, to_json

console = Console()


@click.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--min-score', type=int, default=0,
              help='Minimum passing score (exit 1 if below)')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['text', 'json']),
              default='text',
              help='Output format')
@click.option('--verbose', '-v', is_flag=True,
              help='Show all issues')
@click.version_option()
def main(path: str, min_score: int, output_format: str, verbose: bool):
    """Grade AI-generated tests for quality.

    Examples:

        test-grader ./tests
        test-grader ./tests --min-score 70
        test-grader ./tests --format json
    """
    target_path = Path(path).resolve()

    # Find test files
    test_files = []

    if target_path.is_file():
        test_files = [target_path]
    else:
        # Python tests
        test_files.extend(target_path.rglob('test_*.py'))
        test_files.extend(target_path.rglob('*_test.py'))
        # JavaScript tests
        test_files.extend(target_path.rglob('*.test.js'))
        test_files.extend(target_path.rglob('*.test.ts'))
        test_files.extend(target_path.rglob('*.spec.js'))
        test_files.extend(target_path.rglob('*.spec.ts'))

    # Exclude common directories
    test_files = [f for f in test_files if not any(
        x in f.parts for x in ['node_modules', '.venv', 'venv', '__pycache__']
    )]

    if not test_files:
        console.print("[yellow]No test files found.[/yellow]", file=sys.stderr)
        return

    console.print(f"[dim]Analyzing {len(test_files)} test files...[/dim]", file=sys.stderr)

    # Analyze and score
    scores = []

    for test_file in sorted(test_files):
        if test_file.suffix == '.py':
            metrics = analyze_pytest(test_file)
        else:
            metrics = analyze_jest(test_file)

        score = score_file(
            metrics.path,
            metrics.tests,
            metrics.total_assertions,
            metrics.total_mocks,
        )
        scores.append(score)

    # Output
    if output_format == 'json':
        click.echo(to_json(scores))
    else:
        print_report(scores, console, verbose)

    # Check minimum score
    if min_score > 0:
        avg_score = sum(s.score for s in scores) / len(scores) if scores else 0
        if avg_score < min_score:
            console.print(
                f"[red]Error:[/red] Average score {int(avg_score)} below minimum {min_score}",
                file=sys.stderr
            )
            sys.exit(1)


if __name__ == '__main__':
    main()
