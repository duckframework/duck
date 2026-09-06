"""
Module containing makeproject command class.
"""
import os

from duck.logging import console
from duck.utils.path import joinpaths


class MakeProjectCommand:
    # makeproject command

    @classmethod
    def setup(cls):
        # Setup before command execution
        os.environ["DUCK_SETTINGS_MODULE"] = "duck.etc.structures.projects.testing.web.settings"

    @classmethod
    def main(
        cls,
        name,
        dest_dir: str = ".",
        overwrite_existing: bool = False,
        project_type: str = "normal"
     ):
        # Setup minimum settings module for CLI to function correctly
        cls.setup()
        cls.makeproject(name, dest_dir, overwrite_existing, project_type)

    @classmethod
    def print_success(cls, name, dest_project_path):
        # Nice, low-key welcome block shown after a project is created.
        console.log_raw(f'✓ Project "{name}" created successfully!\n', level=console.SUCCESS)
        console.log_raw(f'  Location:    {dest_project_path}', level=console.SUCCESS)
        console.log_raw(f'  Docs:        https://docs.duckframework.com', level=console.SUCCESS)
        console.log_raw(f'  Contribute:  https://duckframework.com/contribute \n', level=console.SUCCESS)
        console.log_raw(f'Run `python web/main.py` inside "{name}" to get started.\n', level=console.SUCCESS)

    @classmethod
    def makeproject(
        cls,
        name,
        dest_dir: str = ".",
        overwrite_existing: bool = False,
        project_type: str = "normal",
     ):
        # Execute command after setup.
        from duck.setup.makeproject import makeproject

        dest_dir = os.path.abspath(dest_dir)
        dest_project_path = joinpaths(dest_dir, name)
        
        # Project label
        project_label = f'{project_type.title()} Project' if project_type != "normal" else "Project"
        
        # Log initial setup
        console.log(
            f'Creating Duck {project_label} "{name}"...\n',
            level=console.DEBUG,
        )
        
        try:
            makeproject(
                name,
                dest_dir,
                overwrite_existing=overwrite_existing,
                project_type=project_type,
            )
            
            # Print success message
            cls.print_success(name, dest_project_path)

        except FileExistsError:
            console.log(
                f'A project named "{name}" already exists at:\n  {dest_project_path}',
                level=console.WARNING,
            )
            
            # Get input
            overwrite = input("\nOverwrite the existing project? (y/N): ").strip()
            
            # Newline for spacing
            console.log_raw("")
            
            if overwrite.lower().startswith("y"):
                makeproject(
                    name,
                    dest_dir,
                    overwrite_existing=True,
                    project_type=project_type,
                )
                
                # Print success message
                cls.print_success(name, dest_project_path)
                
            else:
                console.log("Cancelled — no changes made.", level=console.DEBUG)

        except Exception as e:
            # Project creation failed.
            console.log(f"Error creating project: {str(e)}", level=console.ERROR)
            raise e
