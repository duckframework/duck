# ⏳ Duck Automations

**Duck** offers powerful automation capabilities that can run tasks throughout your application's lifecycle. With Duck automations, you can schedule tasks to run when specific triggers occur, or you can set them up to run automatically at specified times. 

**These automations are incredibly useful for a variety of purposes, such as:**

- Automatically generating SSL certificates 🔒
- Handling routine maintenance tasks 🛠️
- Managing scheduled backups ⏳
- Triggering notifications or other actions based on specific events 📲

By leveraging Duck's automation framework, you can save time, reduce manual intervention, and ensure critical tasks are handled efficiently and reliably.

To use automations in you Duck web application make sure the following settings are set.

```py
# AUTOMATION SETTINGS
# Automations you would like to run when the application is running.
# This is a mapping of Automation objects as a string to a dictionary with only one allowed key, ie. `trigger`.
# The key `trigger` can be either a class or an object.
# Do help on duck.automations for more info.
# Note: Preparing Automation environment may make the application startup a bit slower.
AUTOMATIONS: dict[str, dict[str, str]] = {
    #"duck.automation.SampleAutomation": {
    #   "trigger": "duck.automation.trigger.NoTrigger",
    # }
}
    
    
# Automation Dispatcher Configuration
# Specifies the class responsible for dispatching automations.
# - You can use a custom dispatcher by subclassing the `AutomationDispatcher` class and implementing the `listen` method.
AUTOMATION_DISPATCHER: str = "duck.automation.dispatcher.DispatcherV1"
    
    
# Run Automations Configuration
# Specifies whether to execute automations when the main application is deployed.
# - When `RUN_AUTOMATIONS=True`, automations will run automatically during deployment.
RUN_AUTOMATIONS: bool = True
```

## Usage and Explanation

The `Automation` class is useful for creating and running tasks with various scheduling options, as well as supporting threading and callback functionalities.

Classes:
- AutomationError: Custom exception for automation-related errors.
- AutomationThread: Threading class for executing automations.
- Automation: Base class for automating tasks, jobs, actions, etc.

### Usage example

The following example shows a simple automation for running a certain `bash` just immediately after
the web application server starts.

#### automations.py

```py
import os
from duck.automation.trigger import NoTrigger # This mean the automation starts immediately

class SimpleAutomation(Automation):
    def execute(self):
        # Execute a shell script
        os.system('bash some_script.sh')

 # Instantiate the automation with specified parameters
 automation = SimpleAutomation(
     name="Sample Automation",
     description="Sample automation",
     start_time='immediate',
     schedules=1,
     interval=0,
)  # Set automation schedules to -1 for infinite schedules
```

#### settings.py

For us to run this automation, we need to add it to settings file as the following:

```py

AUTOMATIONS: dict[str, dict[str, str]] = {
    "automations.SimpleAutomation": { # Simple automation for running simple bash command
           "trigger": "duck.automation.trigger.NoTrigger", # This trigger runs automations immediately after their schedules.
         }
    }
````

## Automation Trigger

This is a condition for starting an `automation`. This may be an event that may trigger this automation, e.g. when 
an `ssl certicate` has expired, an `automation` may be scheduled to be run on this `trigger` (ssl certificate expiration).

You can freely create your custom `trigger` by subclassing the `AutomationTrigger` class and implementing method
`listen`. In `listen` method, return a `boolean` on whether the condition has been met or. This method is constantly 
executed to check immediately whether your `trigger` is satisfied or not.

## Automation Dispatcher

This is the core engine for executing the scheduled automations, usually you do not need to set or 
modify this in `settings.py`.
