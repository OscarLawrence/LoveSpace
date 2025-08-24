"""Commercial CLI main entry point."""

import sys
import click
from pathlib import Path

# Add the OM package to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from om.cli.main import main as om_main
from .cli_wrapper import cli_wrapper
from .onboarding import OnboardingSystem
from .analytics import AnalyticsCollector
from .docs import DocumentationGenerator


@click.group(invoke_without_command=True)
@click.option('--setup', is_flag=True, help='Run setup wizard')
@click.option('--version', is_flag=True, help='Show version')
@click.pass_context
def main(ctx, setup, version):
    """OM Commercial - AI-first monorepo management (Commercial Edition)."""
    
    if version:
        click.echo("OM Commercial v1.0.0")
        return
    
    if setup:
        onboarding = OnboardingSystem()
        success = onboarding.run_setup_wizard()
        sys.exit(0 if success else 1)
    
    # If no command specified, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return
    
    # Validate license before proceeding
    if not cli_wrapper.validate_license_on_startup():
        sys.exit(1)


@main.command()
def usage():
    """Show usage statistics."""
    try:
        analytics = AnalyticsCollector()
        summary = analytics.get_usage_summary(days=30)
        
        click.echo("📊 Usage Summary (Last 30 Days)")
        click.echo(f"Total commands: {summary['total_commands']}")
        click.echo(f"Success rate: {summary['success_rate']:.1%}")
        click.echo(f"Average duration: {summary['avg_duration_ms']:.0f}ms")
        
        if summary['top_commands']:
            click.echo("\nTop Commands:")
            for cmd, count in summary['top_commands'][:5]:
                click.echo(f"  {cmd}: {count}")
        
    except Exception as e:
        click.echo(f"Error retrieving usage data: {e}", err=True)


@main.command()
def health():
    """Show system health metrics."""
    try:
        analytics = AnalyticsCollector()
        health_data = analytics.get_health_metrics()
        
        click.echo("🔧 System Health")
        click.echo(f"Status: {health_data.get('status', 'unknown')}")
        
        if 'avg_cpu_percent' in health_data:
            click.echo(f"Average CPU: {health_data['avg_cpu_percent']:.1f}%")
            click.echo(f"Average Memory: {health_data['avg_memory_mb']:.0f}MB")
        
    except Exception as e:
        click.echo(f"Error retrieving health data: {e}", err=True)


@main.command()
@click.option('--output', type=click.Choice(['console', 'file']), default='console')
def docs_generate(output):
    """Generate customer documentation."""
    try:
        doc_gen = DocumentationGenerator()
        
        # Generate getting started guide
        getting_started = doc_gen.generate_getting_started()
        
        if output == 'file':
            docs_dir = Path.cwd() / "docs"
            docs_dir.mkdir(exist_ok=True)
            
            with open(docs_dir / "getting-started.md", 'w') as f:
                f.write(getting_started)
            
            click.echo(f"Documentation generated in {docs_dir}")
        else:
            click.echo(getting_started)
        
    except Exception as e:
        click.echo(f"Error generating documentation: {e}", err=True)


@main.command()
def support():
    """Create support ticket."""
    click.echo("🎧 OM Commercial Support")
    
    issue = click.prompt("Describe your issue")
    
    try:
        onboarding = OnboardingSystem()
        ticket_id = onboarding.create_support_ticket(issue)
        click.echo(f"Ticket created: {ticket_id}")
        
    except Exception as e:
        click.echo(f"Error creating support ticket: {e}", err=True)


# Import and wrap existing OM commands
def wrap_om_commands():
    """Wrap existing OM commands with commercial functionality."""
    
    # Get original OM command groups
    try:
        from om.cli.workspace import workspace
        from om.cli.docs import docs
        from om.cli.code import code
        from om.cli.find import find
        from om.cli.scaffold import scaffold
        from om.cli.memory import memory
        
        # Wrap commands with commercial checks
        wrapped_workspace = cli_wrapper.wrap_command(workspace, "workspace")
        wrapped_docs = cli_wrapper.wrap_command(docs, "docs") 
        wrapped_code = cli_wrapper.wrap_command(code, "code")
        wrapped_find = cli_wrapper.wrap_command(find, "find")
        wrapped_scaffold = cli_wrapper.wrap_command(scaffold, "scaffold")
        wrapped_memory = cli_wrapper.wrap_command(memory, "memory")
        
        # Add to main CLI
        main.add_command(wrapped_workspace)
        main.add_command(wrapped_docs)
        main.add_command(wrapped_code)
        main.add_command(wrapped_find)
        main.add_command(wrapped_scaffold)
        main.add_command(wrapped_memory)
        
    except ImportError as e:
        # Fallback if OM modules not available
        click.echo(f"Warning: Could not load OM modules: {e}", err=True)


# Initialize wrapped commands
wrap_om_commands()


if __name__ == '__main__':
    main()
