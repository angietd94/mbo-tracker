# Import all routes
from . import auth_routes
from . import dashboard_routes
from . import mbo_routes
from . import user_routes
from . import settings_routes
from . import slack_interactions

# The routes are automatically registered with Flask through the @app.route decorators