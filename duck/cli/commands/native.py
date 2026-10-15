"""
Module containing native command class.
"""
import sys


class NativeCommand:
    # native command
    
    @classmethod
    def setup(cls):
        # Setup before command execution
        pass
    
    @classmethod
    def main(cls):
        cls.setup()
        cls.native()
        
    @classmethod
    def native(cls):
        # Execute command after setup.
        # This command uses sys.argv to retrieve command arguments.
        try:
            from duck_native.cli import cli
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Duck Native is not found, install using 'pip install duck-native' ")
            
        command_args = []
        keyword_reached = False
        
        for arg in sys.argv:
            if not keyword_reached:
                if arg.strip() == "native":
                    keyword_reached = True
            else:
                command_args.append(arg)
        
        # Execute command
        cli.main(prog_name="duck native", args=command_args, standalone_mode=False)
