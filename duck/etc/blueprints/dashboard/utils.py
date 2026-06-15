"""
Utility module for the dashboard blueprint.
"""
import os

from duck.settings import SETTINGS
from duck.utils.safe_compare import constant_time_compare


def check_username_and_pwd(username: str, pwd: str):
    """
    Checks whether the provided username and password matches the configured one.
    """
    corrrect_username = None
    correct_pwd = None
    
    if SETTINGS['DEBUG']:
        correct_username = SETTINGS['DASHBOARD_USERNAME']
        correct_pwd = SETTINGS['DASHBOARD_PWD']
    else:
        correct_username = os.getenv('DASHBOARD_USERNAME')
        correct_pwd = os.getenv('DASHBOARD_PWD')
        
    if not correct_username or not correct_pwd:
        # Username or password not set.
        raise ValueError(
            "Dashboard credentials are not configured. Set DASHBOARD_USERNAME and DASHBOARD_PWD environment variables."
        )
    
    # Compare username and password.    
    return constant_time_compare(correct_username, username) and constant_time_compare(correct_pwd, pwd)
