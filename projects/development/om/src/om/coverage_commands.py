"""Documentation coverage enforcement commands."""

import click
from pathlib import Path
import json

from .coverage_enforcement import CoverageAnalyzer, QualityGate, CoverageReporter
from .scoped_cli import scoped_command, validate_scope


@click.group()
def coverage():
    """Documentation coverage analysis and enforcement."""
    pass


@coverage.command()
@click.argument('source_dir', type=click.Path(exists=True))
@click.option('--patterns', '-p', multiple=True, default=['**/*.py'], help='File patterns to analyze')
@click.option('--output', '-o', help='Output file for coverage report')
@click.option('--format', 'output_format', default='text', type=click.Choice(['text', 'json', 'html']))
@click.option('--min-coverage', type=float, help='Minimum coverage percentage required')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@scoped_command(['docs'])
@validate_scope
def analyze(source_dir, patterns, output, output_format, min_coverage, verbose):
    """Analyze documentation coverage for source directory."""
    analyzer = CoverageAnalyzer()
    
    if min_coverage:
        analyzer.quality_thresholds['min_coverage_percentage'] = min_coverage
    
    click.echo(f"coverage:analyzing:{source_dir}")
    
    # Analyze coverage
    metrics = analyzer.analyze_coverage(Path(source_dir), list(patterns))
    
    # Generate report
    reporter = CoverageReporter()
    
    if output_format == 'json':
        report = reporter.generate_json_report(metrics)
    elif output_format == 'html':
        report = reporter.generate_html_report(metrics)
    else:
        report = reporter.generate_text_report(metrics)
    
    # Output report
    if output:
        with open(output, 'w') as f:
            f.write(report)
        click.echo(f"coverage:report_saved:{output}")
    else:
        click.echo(report)
    
    # Summary output
    click.echo(f"coverage:summary:total:{metrics.total_elements}:documented:{metrics.documented_elements}")
    click.echo(f"coverage:percentage:{metrics.coverage_percentage:.1f}")
    click.echo(f"coverage:quality_score:{metrics.quality_score}")
    click.echo(f"coverage:issues:{len(metrics.issues)}")


@coverage.command()
@click.argument('source_dir', type=click.Path(exists=True))
@click.option('--config', '-c', help='Quality gate configuration file')
@click.option('--min-coverage', type=float, default=80.0, help='Minimum coverage percentage')
@click.option('--min-quality', type=float, default=7.0, help='Minimum quality score')
@click.option('--max-errors', type=int, default=0, help='Maximum allowed errors')
@click.option('--max-warnings', type=int, default=10, help='Maximum allowed warnings')
@scoped_command(['docs'])
@validate_scope
def gate(source_dir, config, min_coverage, min_quality, max_errors, max_warnings):
    """Enforce quality gate for documentation coverage."""
    # Load configuration
    gate_config = {
        'min_coverage': min_coverage,
        'min_quality_score': min_quality,
        'max_errors': max_errors,
        'max_warnings': max_warnings,
        'fail_on_missing_critical': True
    }
    
    if config and Path(config).exists():
        with open(config) as f:
            gate_config.update(json.load(f))
    
    # Analyze coverage
    analyzer = CoverageAnalyzer()
    metrics = analyzer.analyze_coverage(Path(source_dir))
    
    # Check quality gate
    quality_gate = QualityGate(gate_config)
    passed, failures = quality_gate.check_quality_gate(metrics)
    
    # Report results
    click.echo(f"coverage:gate:coverage:{metrics.coverage_percentage:.1f}")
    click.echo(f"coverage:gate:quality:{metrics.quality_score}")
    click.echo(f"coverage:gate:issues:{len(metrics.issues)}")
    
    if passed:
        click.echo("coverage:gate:PASSED")
    else:
        click.echo("coverage:gate:FAILED")
        for failure in failures:
            click.echo(f"coverage:gate:failure:{failure}")
        
        # Exit with error code
        raise click.ClickException("Quality gate failed")


@coverage.command()
@click.argument('source_dir', type=click.Path(exists=True))
@click.option('--output', '-o', required=True, help='Output file for missing docs list')
@click.option('--format', 'output_format', default='text', type=click.Choice(['text', 'json', 'csv']))
@scoped_command(['docs'])
@validate_scope
def missing(source_dir, output, output_format):
    """Generate list of elements missing documentation."""
    analyzer = CoverageAnalyzer()
    metrics = analyzer.analyze_coverage(Path(source_dir))
    
    if output_format == 'json':
        data = {
            'missing_count': len(metrics.missing_docs),
            'missing_elements': metrics.missing_docs,
            'total_elements': metrics.total_elements,
            'coverage_percentage': metrics.coverage_percentage
        }
        content = json.dumps(data, indent=2)
    
    elif output_format == 'csv':
        lines = ['file,element,type']
        for missing in metrics.missing_docs:
            if ':' in missing:
                file_part, element = missing.split(':', 1)
                element_type = 'module' if element == 'module' else 'unknown'
                lines.append(f"{file_part},{element},{element_type}")
        content = '\n'.join(lines)
    
    else:  # text format
        lines = [f"Missing Documentation ({len(metrics.missing_docs)} elements)"]
        lines.append("=" * 50)
        for missing in metrics.missing_docs:
            lines.append(missing)
        content = '\n'.join(lines)
    
    with open(output, 'w') as f:
        f.write(content)
    
    click.echo(f"coverage:missing:saved:{output}")
    click.echo(f"coverage:missing:count:{len(metrics.missing_docs)}")


@coverage.command()
@click.argument('source_dir', type=click.Path(exists=True))
@click.option('--severity', default='warning', type=click.Choice(['error', 'warning', 'info', 'all']))
@click.option('--output', '-o', help='Output file for issues report')
@click.option('--limit', type=int, default=50, help='Maximum number of issues to show')
@scoped_command(['docs'])
@validate_scope
def issues(source_dir, severity, output, limit):
    """Show documentation quality issues."""
    analyzer = CoverageAnalyzer()
    metrics = analyzer.analyze_coverage(Path(source_dir))
    
    # Filter issues by severity
    if severity == 'all':
        filtered_issues = metrics.issues
    else:
        filtered_issues = [issue for issue in metrics.issues if issue['severity'] == severity]
    
    # Limit results
    if limit and len(filtered_issues) > limit:
        filtered_issues = filtered_issues[:limit]
        truncated = True
    else:
        truncated = False
    
    # Format output
    lines = [f"Documentation Issues - {severity.upper()} ({len(filtered_issues)} shown)"]
    lines.append("=" * 60)
    
    for issue in filtered_issues:
        lines.append(f"{issue['file_path']}:{issue['line_number']}")
        lines.append(f"  {issue['element_name']} ({issue['element_type']})")
        lines.append(f"  {issue['issue_type']}: {issue['description']}")
        lines.append("")
    
    if truncated:
        lines.append(f"... {len(metrics.issues) - limit} more issues (use --limit to see more)")
    
    content = '\n'.join(lines)
    
    if output:
        with open(output, 'w') as f:
            f.write(content)
        click.echo(f"coverage:issues:saved:{output}")
    else:
        click.echo(content)
    
    click.echo(f"coverage:issues:total:{len(metrics.issues)}")
    click.echo(f"coverage:issues:shown:{len(filtered_issues)}")


@coverage.command()
@click.argument('config_file', type=click.Path())
@click.option('--min-coverage', type=float, default=80.0)
@click.option('--min-quality', type=float, default=7.0)
@click.option('--max-errors', type=int, default=0)
@click.option('--max-warnings', type=int, default=10)
@scoped_command(['docs'])
@validate_scope
def init_config(config_file, min_coverage, min_quality, max_errors, max_warnings):
    """Initialize coverage configuration file."""
    config = {
        'coverage_rules': {
            'require_module_docs': True,
            'require_class_docs': True,
            'require_public_method_docs': True,
            'require_function_docs': True,
            'allow_private_undocumented': True,
            'min_docstring_length': 10,
            'require_parameter_docs': True,
            'require_return_docs': True,
            'require_examples_for_complex': True
        },
        'quality_thresholds': {
            'min_coverage_percentage': min_coverage,
            'max_complexity_undocumented': 5,
            'min_docstring_quality_score': min_quality,
            'max_issues_per_file': 10
        },
        'quality_gate': {
            'min_coverage': min_coverage,
            'min_quality_score': min_quality,
            'max_errors': max_errors,
            'max_warnings': max_warnings,
            'fail_on_missing_critical': True
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    click.echo(f"coverage:config:created:{config_file}")


# Register with docs commands
def register_coverage_commands(docs_group):
    """Register coverage commands with docs group."""
    docs_group.add_command(coverage)