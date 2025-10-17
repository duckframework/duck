"""
Module containing django command class.
"""
import sys


class DjangoCommand:
    # django command
    
    @classmethod
    def setup(cls):
        # Setup before command execution
        pass
    
    @classmethod
    def main(cls):
        cls.setup()
        cls.django()
        
    @classmethod
    def django(cls):
        # Execute command after setup.
        # This command uses sys.argv to retrieve command arguments.
        from duck.backend.django.utils import execute_from_command_line
        
        command_args = []
        
        keyword_reached = False
        for arg in sys.argv:
            if not keyword_reached:
                if arg.strip() == "django":
                    keyword_reached = True
            else:
                command_args.append(arg)
        
        command = ["manage.py", *command_args]
        execute_from_command_line(command)
