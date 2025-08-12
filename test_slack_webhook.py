#!/usr/bin/env python3
"""
Test Slack Webhook

A simple script to test if your Slack webhook URL is working correctly.
Run this before using the main LinkedIn scraper to ensure Slack integration works.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Update this with your webhook URL
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

def test_slack_webhook(webhook_url: str) -> bool:
    """
    Test the Slack webhook by sending a test message.
    
    Args:
        webhook_url: The Slack webhook URL to test
        
    Returns:
        bool: True if test successful, False otherwise
    """
    # Validate webhook URL
    if webhook_url == "https://hooks.slack.com/services/YOUR/WEBHOOK/URL":
        print("❌ Error: Please update SLACK_WEBHOOK_URL with your actual webhook URL")
        return False
    
    if not webhook_url.startswith("https://hooks.slack.com/services/"):
        print("❌ Error: Invalid Slack webhook URL format")
        return False
    
    # Prepare test message
    test_message = {
        "text": f"🧪 Test message from LinkedIn Notification Scraper - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "username": "LinkedIn Notification Bot",
        "icon_emoji": ":bell:"
    }
    
    try:
        print("📤 Sending test message to Slack...")
        response = requests.post(
            webhook_url,
            json=test_message,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Success! Test message sent to Slack successfully.")
            print("📱 Check your Slack channel to confirm the message was received.")
            return True
        else:
            print(f"❌ Failed to send message. HTTP Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Check your internet connection.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function to run the webhook test."""
    print("🔗 LinkedIn Notification Scraper - Slack Webhook Test")
    print("=" * 50)
    
    # Test the webhook
    success = test_slack_webhook(SLACK_WEBHOOK_URL)
    
    if success:
        print("\n🎉 Webhook test completed successfully!")
        print("You can now run the main LinkedIn scraper script.")
    else:
        print("\n🔧 Please fix the webhook configuration and try again.")
        print("\nTroubleshooting tips:")
        print("1. Verify your webhook URL is correct")
        print("2. Check your Slack app has incoming webhook permissions")
        print("3. Ensure your internet connection is working")
        print("4. Test the webhook manually with curl:")
        print(f'   curl -X POST -H "Content-type: application/json" \\')
        print(f'        --data \'{{"text":"Manual test"}}\' \\')
        print(f'        "{SLACK_WEBHOOK_URL}"')
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)