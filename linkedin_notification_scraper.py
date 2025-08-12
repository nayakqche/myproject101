#!/usr/bin/env python3
"""
LinkedIn Notification Scraper

This script connects to an existing browser session with LinkedIn already open,
scrapes the "Mentions" notification filters and their statuses, and sends 
the results to a Slack channel via webhook.

Requirements:
- LinkedIn notification preferences page should be open in browser
- Browser session should already be authenticated
- Slack webhook URL should be configured

Author: Assistant
"""

import json
import logging
import time
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests


# Configuration
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"  # Replace with your webhook URL
LINKEDIN_MENTIONS_URL = "https://www.linkedin.com/mypreferences/d/categories/notifications"
WAIT_TIMEOUT = 10  # seconds


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinkedInNotificationScraper:
    """Scrapes LinkedIn notification preferences and sends results to Slack."""
    
    def __init__(self, slack_webhook_url: str = SLACK_WEBHOOK_URL):
        """
        Initialize the scraper.
        
        Args:
            slack_webhook_url: The Slack webhook URL for sending messages
        """
        self.slack_webhook_url = slack_webhook_url
        self.driver = None
        self.wait = None
    
    def connect_to_existing_browser(self) -> bool:
        """
        Connect to an existing Chrome browser session.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Chrome options for connecting to existing session
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            # Connect to existing browser session
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)
            
            logger.info("Successfully connected to existing browser session")
            return True
            
        except WebDriverException as e:
            logger.error(f"Failed to connect to existing browser session: {e}")
            logger.error("Make sure Chrome is running with --remote-debugging-port=9222")
            return False
    
    def navigate_to_mentions_page(self) -> bool:
        """
        Navigate to the LinkedIn mentions notification page.
        
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            logger.info("Navigating to LinkedIn mentions notification page...")
            self.driver.get(LINKEDIN_MENTIONS_URL)
            
            # Wait for page to load
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info("Successfully navigated to mentions page")
            return True
            
        except TimeoutException:
            logger.error("Timeout waiting for page to load")
            return False
        except WebDriverException as e:
            logger.error(f"Failed to navigate to mentions page: {e}")
            return False
    
    def scrape_mentions_filters(self) -> Dict[str, str]:
        """
        Scrape the mentions notification filters and their statuses.
        
        Returns:
            Dict[str, str]: Dictionary mapping filter names to their statuses
        """
        filters = {}
        
        try:
            logger.info("Scraping mentions notification filters...")
            
            # Wait for the page content to load
            time.sleep(3)
            
            # Look for notification preference items
            # LinkedIn uses various selectors, so we'll try multiple approaches
            selectors_to_try = [
                "[data-test-id*='notification']",
                "[class*='notification']",
                "[class*='preference']",
                ".artdeco-list__item",
                "[role='listitem']"
            ]
            
            elements_found = False
            
            for selector in selectors_to_try:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        elements_found = True
                        
                        for element in elements:
                            filter_name, status = self._extract_filter_info(element)
                            if filter_name and status:
                                filters[filter_name] = status
                        
                        if filters:
                            break
                            
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not elements_found:
                # Try alternative approach - look for toggle switches and labels
                self._try_alternative_scraping(filters)
            
            if not filters:
                # Fallback: get page source for manual inspection
                logger.warning("No filters found with standard selectors")
                self._log_page_info()
            
        except Exception as e:
            logger.error(f"Error scraping mentions filters: {e}")
        
        logger.info(f"Found {len(filters)} notification filters")
        return filters
    
    def _extract_filter_info(self, element) -> tuple:
        """
        Extract filter name and status from a web element.
        
        Args:
            element: Selenium WebElement
            
        Returns:
            tuple: (filter_name, status) or (None, None) if extraction failed
        """
        try:
            # Look for text content that might contain filter name
            text_content = element.text.strip()
            
            if not text_content or len(text_content) < 3:
                return None, None
            
            # Look for toggle switches or status indicators
            toggle_elements = element.find_elements(By.CSS_SELECTOR, 
                "[role='switch'], input[type='checkbox'], .toggle, [class*='switch']")
            
            status = "Unknown"
            
            if toggle_elements:
                toggle = toggle_elements[0]
                
                # Check various attributes that might indicate status
                if toggle.get_attribute("aria-checked"):
                    status = "Enabled" if toggle.get_attribute("aria-checked") == "true" else "Disabled"
                elif toggle.get_attribute("checked"):
                    status = "Enabled" if toggle.get_attribute("checked") else "Disabled"
                elif "checked" in toggle.get_attribute("class") or "":
                    status = "Enabled"
                elif "unchecked" in toggle.get_attribute("class") or "":
                    status = "Disabled"
            
            # Clean up filter name
            filter_name = text_content.split('\n')[0]  # Take first line
            filter_name = filter_name.replace('Toggle', '').replace('switch', '').strip()
            
            if len(filter_name) > 3 and filter_name not in ['On', 'Off', 'Enabled', 'Disabled']:
                return filter_name, status
            
        except Exception as e:
            logger.debug(f"Error extracting filter info: {e}")
        
        return None, None
    
    def _try_alternative_scraping(self, filters: Dict[str, str]):
        """
        Alternative scraping approach for different page layouts.
        
        Args:
            filters: Dictionary to populate with found filters
        """
        try:
            # Look for labels and their associated controls
            labels = self.driver.find_elements(By.TAG_NAME, "label")
            
            for label in labels:
                try:
                    label_text = label.text.strip()
                    if len(label_text) > 3:
                        # Look for associated input/toggle
                        label_for = label.get_attribute("for")
                        if label_for:
                            toggle = self.driver.find_element(By.ID, label_for)
                            if toggle:
                                status = "Enabled" if toggle.get_attribute("checked") else "Disabled"
                                filters[label_text] = status
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Alternative scraping failed: {e}")
    
    def _log_page_info(self):
        """Log page information for debugging purposes."""
        try:
            page_title = self.driver.title
            current_url = self.driver.current_url
            
            logger.info(f"Current page title: {page_title}")
            logger.info(f"Current URL: {current_url}")
            
            # Log some page structure for debugging
            body_text = self.driver.find_element(By.TAG_NAME, "body").text[:500]
            logger.debug(f"Page content preview: {body_text}...")
            
        except Exception as e:
            logger.debug(f"Error logging page info: {e}")
    
    def send_to_slack(self, filters: Dict[str, str]) -> bool:
        """
        Send the scraped filter information to Slack.
        
        Args:
            filters: Dictionary of filter names and statuses
            
        Returns:
            bool: True if all messages sent successfully, False otherwise
        """
        if not filters:
            logger.warning("No filters to send to Slack")
            return False
        
        success_count = 0
        
        for filter_name, status in filters.items():
            message = f"Filter Name: {filter_name}: {status}"
            
            payload = {
                "text": message,
                "username": "LinkedIn Notification Bot",
                "icon_emoji": ":bell:"
            }
            
            try:
                response = requests.post(
                    self.slack_webhook_url,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully sent to Slack: {message}")
                    success_count += 1
                else:
                    logger.error(f"Failed to send to Slack: {response.status_code} - {response.text}")
                
                # Small delay between messages to avoid rate limiting
                time.sleep(0.5)
                
            except requests.RequestException as e:
                logger.error(f"Error sending message to Slack: {e}")
        
        logger.info(f"Successfully sent {success_count}/{len(filters)} messages to Slack")
        return success_count == len(filters)
    
    def run(self) -> bool:
        """
        Main execution method that orchestrates the scraping and sending process.
        
        Returns:
            bool: True if process completed successfully, False otherwise
        """
        try:
            # Connect to existing browser
            if not self.connect_to_existing_browser():
                return False
            
            # Navigate to mentions page (optional if already there)
            if not self.navigate_to_mentions_page():
                logger.warning("Failed to navigate, continuing with current page...")
            
            # Scrape the filters
            filters = self.scrape_mentions_filters()
            
            if not filters:
                logger.error("No notification filters found")
                return False
            
            # Send to Slack
            return self.send_to_slack(filters)
            
        except Exception as e:
            logger.error(f"Unexpected error during execution: {e}")
            return False
        
        finally:
            # Note: We don't close the driver since we're using an existing session
            logger.info("Scraping process completed")
    
    def close(self):
        """Clean up resources (optional, since we're using existing session)."""
        if self.driver:
            # Don't quit the driver since we're using an existing session
            # self.driver.quit()
            logger.info("Disconnected from browser session")


def main():
    """Main entry point for the script."""
    logger.info("Starting LinkedIn Notification Scraper...")
    
    # Validate webhook URL
    if SLACK_WEBHOOK_URL == "https://hooks.slack.com/services/YOUR/WEBHOOK/URL":
        logger.error("Please configure your Slack webhook URL in the SLACK_WEBHOOK_URL variable")
        return False
    
    # Create and run scraper
    scraper = LinkedInNotificationScraper(SLACK_WEBHOOK_URL)
    
    try:
        success = scraper.run()
        if success:
            logger.info("Script completed successfully!")
        else:
            logger.error("Script completed with errors")
        return success
        
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
        return False
    
    finally:
        scraper.close()


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)