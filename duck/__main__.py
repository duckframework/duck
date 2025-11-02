#!/usr/bin/env python
"""
Main entry to Duck command-line tool.
"""
import os
import sys
import click
import setproctitle

from duck.art import duck_art_small
from duck.version import server_version
from duck.logging import console

from duck.cli.commands.collectstatic import CollectStaticCommand
from duck.cli.commands.makeproject import MakeProjectCommand
from duck.cli.commands.makeblueprint import MakeBlueprintCommand
from duck.cli.commands.django import DjangoCommand
from duck.cli.commands.runserver import RunserverCommand
from duck.cli.commands.runtests import RuntestsCommand
from duck.cli.commands.ssl_gen import SSLGenCommand
from duck.cli.commands.service import ServiceCommand
from duck.cli.commands.integration import DjangoAddCommand
from duck.cli.commands.logs import LogsCommand
from duck.cli.commands.monitor import MonitorCommand


EXAMPLES = f"""
Examples:
    python3 -m duck runserver -a 127.0.0.1 -p 8000
    python3 -m duck makeproject myproject -d ./projects
    python3 -m duck makeblueprint myapp
    python3 -m duck ssl-gen
    python3 -m duck django migrate
    python3 -m duck collectstatic
    python3 -m django-add django_project_path
    
{console.Fore.YELLOW}Commands requiring execution inside the project directory
or with DUCK_SETTINGS_MODULE set: {console.Style.RESET_ALL}
   
   duck collectstatic ...
   duck django ...
   duck ssl-gen ...
   duck runserver ... (Use --file or --settings to bypass this requirement)
   duck django-add ...
   duck logs ...
   ...etc
"""

@click.group(invoke_without_command=True)
@click.option('-V', '--version', is_flag=True, help="Show the version and exit.")
@click.pass_context
def cli(ctx, version):
    """
    Duck CLI - Manage your projects with ease.
    """
    subcommand = ctx.invoked_subcommand
    
    if subcommand:
        # Set process name dynamically
        setproctitle.setproctitle(f"duck-{subcommand}")
    
    if version:
        # Show the version
        click.echo(server_version)
    elif not ctx.invoked_subcommand:
        # Print usage if no subcommands are invoked
        click.echo(click.style(duck_art_small, fg='white', bold=True))
        click.echo(ctx.get_help())
        click.echo(EXAMPLES)


@cli.command()
@click.option('-y', '--skip-confirmation', is_flag=True, default=False, help="Skip confirmation prompts")
def collectstatic(skip_confirmation):
    """
    Collect static files from Blueprints' directories.
    """
    CollectStaticCommand.main(skip_confirmation)


@cli.command(help="Create a Duck project")
@click.argument("name")
@click.option("-d", "--dest", default=".", help="The destination directory to place the project (default: current directory)")
@click.option("-O", "--overwrite", is_flag=True, help="Overwrite an existing project.")
@click.option('--mini', 'project_type', flag_value="mini", help="Create project with minimum files and configuration")
@click.option('--full', 'project_type', flag_value="full", help="Create project with complete files and configuration.")
@click.option('--project-type', default='normal', type=click.Choice(["normal", "full", "mini"]), help="Specify project type")
def makeproject(name, dest, overwrite, project_type):
    """
    Create a new project whether it's a normal, full or a mini project.
    """
    project_type = project_type or "normal"
    MakeProjectCommand.main(name, dest_dir=dest, overwrite_existing=overwrite, project_type=project_type)


@cli.command(help="Create a Duck blueprint directory structure")
@click.argument("name")
@click.option("-d", "--dest", default=".", help="Destination for blueprint creation.")
@click.option("-O", "--overwrite", is_flag=True, help="Overwrite an existing blueprint.")
def makeblueprint(name, dest, overwrite):
   """
   Create a new Blueprint for organizing routes, similar to Flask's Blueprint system.
   
   Notes:
   - It's recommended to provide camelCased names like `CounterApp`.
   """
   MakeBlueprintCommand.main(name, destination=dest, overwrite_existing=overwrite)


@cli.command(help="Execute Django management commands for your project", context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)  # Accept multiple arguments
def django(args):
    """
    Run Django-related commands in your project.
    """
    DjangoCommand.main()


@cli.command(help="Start the development/production server")
@click.option("-a","--address", default="0.0.0.0", help="The address to bind the server to (default: 0.0.0.0)")
@click.option("-p", "--port", type=int, default=8000, help="The port to listen on (default: 8000)")
@click.option( "-d", "--domain", default=None, help="The domain name for the server (optional)")
@click.option("-s", "--settings", default=None, help="The settings module to use (optional)")
@click.option("-f", "--file", default=None, help="The main python file containing app instance (optional)")
@click.option("--ipv6", is_flag=True, default=False, help="Run application using IPV6 (optional)")
@click.option("-dj", "--use-django", is_flag=True, default=False, help="Run application along with Django server. This overrides setting USE_DJANGO in settings.py (optional)")
@click.option("--is-reload", is_flag=True, default=False, help="Flag the application to be in a reload state. Usually set by DuckSightReloader.")
def runserver(address, port, domain, settings, ipv6, file, use_django, is_reload):
    """
    Run the development or production server.
    """
    _ = is_reload
    
    if use_django:
        os.environ.setdefault("DUCK_USE_DJANGO", "true")
        
    RunserverCommand.main(
        address=address,
        port=port,
        domain=domain,
        settings_module=settings,
        mainfile=file,
        uses_ipv6=ipv6,
    )


@cli.command(help="Run default tests using unittest module")
@click.option("-v", "--verbose", default=False, is_flag=True, help="More verbose tests by enabling printing to the console.")
def runtests(verbose):
    """
    Run pre-built Duck test cases.
    """
    RuntestsCommand.main(verbose)


@cli.command(help="Generate a self-signed SSL certificate")
def ssl_gen():
    """
    Generate self-signed SSL certificate.
    """
    SSLGenCommand.main()


@cli.command(help="Integrate an existing Django project into Duck")
@click.argument("source") 
@click.option("-an", "--appname", default=None, help="The Django main app name, useful if main app name is different from project name (optional)")
@click.option("-d", "--dest", default="duckapp", help="The destination name for the project when it's copied (optional). Defaults to 'duckapp' ")
def django_add(source, appname, dest):
    """
    Integrate an existing Django project into Duck.
    """
    DjangoAddCommand.main(source, appname, dest)
    

@cli.group()
def service():
    """
    Create and manage Duck background service for linux-based systems using systemd.
    
    CUSTOMIZE the service in settings.py.
    """

@cli.group()
def logs():
    """
    Manage Duck project logs.
    """
    pass


@cli.command(help="Real-time system monitor for Duck processes")
@click.option('--interval', default=1.0, help="Refresh interval in seconds")
@click.option('--duck-process', default="duck*", help="Partial name of Duck processes to monitor (wildcards supported)")
@click.option('--pid', type=int, multiple=True, help="Specific Duck process IDs to monitor instead of name")
@click.option('--cpu-warning', default=80.0, help="CPU usage threshold for warning highlight")
@click.option('--ram-warning', default=80.0, help="RAM usage threshold for warning highlight")
def monitor(interval, duck_process, pid, cpu_warning, ram_warning):
    """
    Monitor Duck system metrics in real-time.

    Supports:
    - Multiple Duck servers by name
    - Filtering by specific process IDs
    - CPU/RAM threshold highlighting
    """
    MonitorCommand.main(
        interval=interval,
        duck_process_name=duck_process,
        duck_pids=list(pid) if pid else None,
        cpu_warning=cpu_warning,
        ram_warning=ram_warning
    )


# Register subcommands the duck commands.
ServiceCommand.register_subcommands(main_command=service)
LogsCommand.register_subcommands(main_command=logs)


if __name__ == "__main__":
    cli()