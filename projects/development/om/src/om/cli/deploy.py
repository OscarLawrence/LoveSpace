"""
OM Deploy CLI - Pure Logic Interface
Eliminates built-in tool chaos through unified OM commands.
"""

import click
from ..deployment import deploy_collaboration_platform, check_platform_status


@click.group()
def deploy():
    """OM deployment commands - zero inconsistencies."""
    pass


@deploy.command()
@click.option('--platform', default='railway', 
              type=click.Choice(['railway', 'render', 'heroku', 'vercel']),
              help='Deployment platform')
def live(platform):
    """Deploy live collaboration platform through OM."""
    click.echo(f"🚀 Deploying live collaboration platform to {platform}...")
    
    result = deploy_collaboration_platform(platform)
    
    if result.success:
        click.echo(f"✅ Deployment successful!")
        if result.url:
            click.echo(f"🌐 Live at: {result.url}")
        click.echo(f"📊 Platform: {result.platform}")
    else:
        click.echo(f"❌ Deployment failed: {result.error}")
        if result.logs:
            click.echo("📋 Logs:")
            for log in result.logs:
                click.echo(log)


@deploy.command()
@click.argument('url')
def check(url):
    """Check live platform status through OM."""
    click.echo(f"🔍 Checking platform status: {url}")
    
    status = check_platform_status(url)
    
    if status['accessible']:
        click.echo(f"✅ Platform accessible")
        click.echo(f"⚡ Response time: {status['response_time']:.2f}s")
        click.echo(f"📊 Status code: {status['status_code']}")
    else:
        click.echo(f"❌ Platform not accessible")
        if 'error' in status:
            click.echo(f"🔥 Error: {status['error']}")


@deploy.command()
def status():
    """Show deployment history through OM."""
    from ..deployment import OMDeployment
    
    deployer = OMDeployment()
    status = deployer.get_deployment_status()
    
    click.echo("📊 OM Deployment Status")
    click.echo(f"Total deployments: {status['total_deployments']}")
    click.echo(f"Successful: {status['successful_deployments']}")
    click.echo(f"Platforms used: {', '.join(status['platforms_used'])}")
    
    if status['latest_deployment']:
        latest = status['latest_deployment']
        click.echo(f"\n🚀 Latest Deployment:")
        click.echo(f"Platform: {latest.platform}")
        click.echo(f"Success: {'✅' if latest.success else '❌'}")
        if latest.url:
            click.echo(f"URL: {latest.url}")


if __name__ == '__main__':
    deploy()