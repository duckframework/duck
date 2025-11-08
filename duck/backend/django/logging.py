"""
Logging configuration for Django, ensuring compatibility with Duck logs.
"""
from duck.logging import logger
from duck.settings import SETTINGS
from duck.env import is_testing_environment


HANDLERS = ["error_console"]


# Simple Logging Configuration,
# This only log exceptions to console and to file (if LOG_TO_FILE=True) and then
# Duck will handle the rest of the logs (e.g. responses)
SIMPLE_CONFIG  = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "exception_only": {
            "format": "{message}",
            "style": "{"
        }
    },
    "handlers": {
        "error_console": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
            "formatter": "exception_only",
        },
    },
    "loggers": {
        "django": {
            "handlers": HANDLERS,
            "level": "ERROR",
            "propagate": True,
        },
        # Disable other default loggers if needed
        'django.server': {
            'handlers': HANDLERS,
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


if SETTINGS["DJANGO_SILENT"]:
    HANDLERS = ["null"]

    SIMPLE_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "exception_only": {
                "format": "{message}",
                "style": "{"
            }
        },
        "handlers": {
            "null": {
                "class": "logging.NullHandler",
            },
        },
        "loggers": {
            "django": {"handlers": ["null"], "propagate": True},
            "django.request": {"handlers": ["null"], "propagate": False},
            "django.server": {"handlers": ["null"], "propagate": False},
            "": {"handlers": ["null"], "propagate": False},  # Catch all
        },
    }


if SETTINGS["LOG_TO_FILE"] and not is_testing_environment():
    LATEST_LOGFILE = logger.Logger.get_current_logfile()
    
    # Edit handlers
    HANDLERS.append("error_file")
    
    # Add the error_file handler
    SIMPLE_CONFIG["handlers"]["error_file"] = {
        "level": "ERROR",
        "class": "logging.FileHandler",
        "filename": LATEST_LOGFILE,
        "formatter": "exception_only",
    }

    # Edit handlers for available loggers
    for key in SIMPLE_CONFIG["loggers"].keys():
        SIMPLE_CONFIG['loggers'][key]["handlers"].append("error_file")
