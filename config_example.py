"""
Example configuration file for LinkedIn Notification Scraper

Copy this file to config.py and update with your actual values.
"""

# Slack Configuration
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/TEAM/WEBHOOK"

# LinkedIn Configuration
LINKEDIN_MENTIONS_URL = "https://www.linkedin.com/mypreferences/d/categories/notifications"

# Browser Configuration
CHROME_DEBUG_PORT = 9222
CHROME_DEBUG_ADDRESS = "127.0.0.1"

# Scraping Configuration
WAIT_TIMEOUT = 10  # seconds
PAGE_LOAD_DELAY = 3  # seconds

# Slack Message Configuration
SLACK_USERNAME = "LinkedIn Notification Bot"
SLACK_ICON_EMOJI = ":bell:"

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR