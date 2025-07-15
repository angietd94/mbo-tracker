"""
Notifications package for MBO Tracker.
"""

from .slack_improved import send_slack_notification

# Import init_app from the parent notifications.py file
import importlib.util
import os

# Get the path to the notifications.py file in the parent directory
notifications_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'notifications.py')
spec = importlib.util.spec_from_file_location("app_notifications_module", notifications_file_path)
app_notifications_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_notifications_module)

# Import the init_app function
init_app = app_notifications_module.init_app

# Alias for backward compatibility
send_notification = send_slack_notification

__all__ = ['send_slack_notification', 'send_notification', 'init_app']