"""
Module containing the SitemapCommand class for Duck project.
"""
import os
import sys
import click

from typing import List, Optional

from duck.logging import console
from duck.utils.path import joinpaths


class SitemapCommand:
    """
    CLI command group for sitemap command.
    """
    @classmethod
    def create(
        cls,
        server_url: str = None,
        filepath: Optional[str] = None,
        save: bool = True,
        extra_urls: Optional[str] = None,
        exclude: Optional[str] = None,
        priority: Optional[float] = 0.5,
        frequency: Optional[str] = "monthly",
        view: bool = False,
        apply_default_excludes: bool = True,
    ):
        from duck.settings import SETTINGS
        from duck.settings.loaded import SettingsLoaded
        from duck.contrib.sitemap import SitemapBuilder, DEFAULT_EXCLUDES
        from duck.routes import register_urlpatterns, register_blueprints
        from duck.backend.django.setup import prepare_django
        
        extra_urls = [i.strip() for i in (extra_urls or "").split(',')]
        exclude_patterns = [i.strip() for i in (exclude or "").split(',')]
        filepath = filepath or joinpaths(SETTINGS['BASE_DIR'], "etc/sitemap.xml")
        
        console.log("Creating Sitemap", level=console.DEBUG)
        console.log(f"Server root URL: {server_url}\n", level=console.DEBUG)
        console.log(f"Excludes: \n{exclude_patterns}\n", level=console.DEBUG)
        console.log(f"Default Excludes: \n{DEFAULT_EXCLUDES if apply_default_excludes else []}\n", level=console.DEBUG)
        
        if not server_url:
            console.log("Server URL not provided", level=console.WARNING)
            server_url = input("Enter server URL (e.g. https://duckframework.xyz): ")
            server_url = server_url.strip()
            
            if not server_url:
                console.log("Server URL not provided, exitting...", level=console.WARNING)
                sys.exit(1)
            else:
                console.log_raw("")
                
        try:
            # Prepare Django just in case urlpatterns depend on Django models
            try:
                prepare_django(True)
            except Exception as e:
                logger.log_exception(e)
                   
            # Register urlpatterns first
            register_urlpatterns(SettingsLoaded.URLPATTERNS)
            register_blueprints(SettingsLoaded.BLUEPRINTS)
            
            # Continue building sitemap
            builder = SitemapBuilder(
                server_url=server_url, # Parsing None will automatically resolve server URL
                save_to_file=save,
                filepath=filepath,
                extra_urls=extra_urls,
                exclude_patterns=exclude_patterns,
                default_priority=priority,
                default_changefreq=frequency,
                apply_default_excludes=apply_default_excludes,
            )
            xml = builder.build()
            if save:
                    console.log(f"Sitemap saved at {filepath}\n", level=console.SUCCESS)
            if view:
                console.log_raw(xml)
        except Exception as e:
            console.log(f"Error building sitemap: {e}", level=console.WARNING)
            console.log_exception(e)
            
    @classmethod
    def register_subcommands(cls, main_command: click.Command):
        """
        Register the log management subcommands.
        """
        data = {
            "create": {
                "callback": cls.create,
                "params": [
                    click.Option(("-su", "--server-url"), is_flag=False, default=None, help="The server URL. If not provided, it will be resolved automatically."),
                    click.Option(("-f", "--filepath"), is_flag=False, default=None, help="The filepath for the sitemap. If not provided, default will be used."),
                    click.Option(("-s", "--save"), is_flag=False, default=True, help="Whether to save the sitemap to file."),
                    click.Option(("-extra", "--extra-urls"), is_flag=False, default=None, help="Comma-separated extra URLs/paths to add to sitemap."),
                    click.Option(("-e", "--exclude"), is_flag=False, default=None, help="Comma-separated regex patterns to exclude from final URLs."),
                    click.Option(("-p", "--priority"), is_flag=False, default=0.5, help="Default priority. Defaults to 0.5."),
                    click.Option(("-fq", "--frequency"), is_flag=False, default="monthly", help="The frequency of updates. Defaults to 'monthly'."),
                    click.Option(("-cat", "--view"), is_flag=True, default=False, help="View generated sitemap."),
                    click.Option(("-de", "--apply-default-excludes"), is_flag=False, default=True, help="Whether to apply default exclude patterns on top of your excludes. Defaults to True."),
                ],
                "help": "Generate a sitemap."
            },
        }
        
        for cmd_name, info in data.items():
            cmd = click.Command(cmd_name, callback=info["callback"], params=info["params"], help=info["help"])
            main_command.add_command(cmd)
