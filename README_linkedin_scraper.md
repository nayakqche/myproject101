# LinkedIn Notification Scraper

A Python script that connects to an existing browser session, scrapes LinkedIn mention notification preferences, and sends the results to a Slack channel via webhook.

## Features

- ✅ Connects to existing authenticated browser session (no re-authentication needed)
- ✅ Scrapes LinkedIn "Mentions" notification filter preferences
- ✅ Sends individual filter results to Slack via webhook
- ✅ Robust error handling and logging
- ✅ Multiple scraping strategies for different page layouts
- ✅ Clean, well-documented code

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Google Chrome** browser
3. **ChromeDriver** (compatible with your Chrome version)
4. **Slack webhook URL** for your target channel
5. **LinkedIn account** with access to notification preferences

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Install ChromeDriver:
   - **Option A**: Download from [ChromeDriver Downloads](https://chromedriver.chromium.org/)
   - **Option B**: Use package manager:
     ```bash
     # On macOS with Homebrew
     brew install chromedriver
     
     # On Ubuntu/Debian
     sudo apt-get install chromium-chromedriver
     
     # On Windows with Chocolatey
     choco install chromedriver
     ```

3. Ensure ChromeDriver is in your PATH or place it in the same directory as the script.

## Setup

### 1. Configure Slack Webhook

1. Go to your Slack workspace and create a new incoming webhook:
   - Visit https://api.slack.com/incoming-webhooks
   - Click "Create your Slack app"
   - Choose "From scratch" and configure your app
   - Add incoming webhook feature
   - Copy the webhook URL

2. Update the script configuration:
   ```python
   SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
   ```

### 2. Prepare Browser Session

1. **Start Chrome with remote debugging enabled:**
   ```bash
   # On Windows
   chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_debug"
   
   # On macOS
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_debug"
   
   # On Linux
   google-chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_debug"
   ```

2. **Navigate to LinkedIn and log in:**
   - Open https://linkedin.com in the Chrome instance
   - Log in to your LinkedIn account
   - Navigate to: https://www.linkedin.com/mypreferences/d/categories/notifications
   - Leave this tab open

## Usage

### Basic Usage

```bash
python linkedin_notification_scraper.py
```

### Advanced Usage

You can customize the script behavior by modifying the configuration variables:

```python
# Configuration options
SLACK_WEBHOOK_URL = "your_webhook_url_here"
LINKEDIN_MENTIONS_URL = "https://www.linkedin.com/mypreferences/d/categories/notifications"
WAIT_TIMEOUT = 10  # seconds to wait for page elements
```

### Programmatic Usage

```python
from linkedin_notification_scraper import LinkedInNotificationScraper

# Initialize scraper
scraper = LinkedInNotificationScraper("your_webhook_url")

# Run the scraping process
success = scraper.run()

if success:
    print("Scraping completed successfully!")
else:
    print("Scraping failed - check logs for details")
```

## Output Format

Each notification filter is sent to Slack in the format:
```
Filter Name: [Filter Name]: [Status]
```

Example:
```
Filter Name: Someone mentions you in a post: Enabled
Filter Name: Someone mentions you in a comment: Disabled
```

## Troubleshooting

### Common Issues

1. **"Failed to connect to existing browser session"**
   - Ensure Chrome is running with `--remote-debugging-port=9222`
   - Check that port 9222 is not blocked by firewall
   - Verify the Chrome process is actually running

2. **"No notification filters found"**
   - Ensure you're on the correct LinkedIn page
   - Try refreshing the page manually
   - Check if LinkedIn has changed their page structure
   - Review debug logs for page content information

3. **"Slack webhook errors"**
   - Verify your webhook URL is correct
   - Test the webhook URL manually with curl:
     ```bash
     curl -X POST -H 'Content-type: application/json' \
       --data '{"text":"Test message"}' \
       YOUR_WEBHOOK_URL
     ```

4. **ChromeDriver issues**
   - Ensure ChromeDriver version matches your Chrome version
   - Check that ChromeDriver is in your PATH
   - Try updating ChromeDriver to the latest version

### Debug Mode

Enable debug logging by modifying the logging level:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Manual Page Inspection

If the script can't find elements, you can inspect the page structure:

1. Open Chrome DevTools (F12) on the LinkedIn notifications page
2. Look for elements containing notification preferences
3. Update the `selectors_to_try` list in the script with new selectors

## Security Considerations

- The script connects to an existing browser session - ensure your LinkedIn session is secure
- Webhook URLs should be kept private and not committed to version control
- Consider using environment variables for sensitive configuration:

```python
import os
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', 'default_url')
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is provided as-is for educational and automation purposes. Please ensure compliance with LinkedIn's Terms of Service and robots.txt when using this script.