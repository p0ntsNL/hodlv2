"""
Default configuration file for the database, webinterface and logging.
Updating this configuration file is for advanced users only.
"""

# MongoDB host settings  (default: 127.0.0.1:27017)
MONGODB_HOST = "127.0.0.1"
MONGODB_PORT = 27017

# Webinterface settings (default: 0.0.0.0:8080)
WEB_HOST = "0.0.0.0"
WEB_PORT = 8080
WEB_FLASK_SECRET = "update-this-secret-for-session-security"

# Logging settings
LOGLEVEL = "INFO"
