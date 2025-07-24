"""
URL scraping functionality for Google Ads copy generator.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import time
from utils import clean_text, is_valid_url


class WebScraper:
    """Web scraper for extracting content from target URLs."""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize the web scraper.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_url(self, url: str) -> Dict[str, str]:
        """
        Scrape content from a target URL.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dict containing scraped content with keys:
            - title: Page title
            - meta_description: Meta description
            - h1: H1 heading
            - h2_h3: Combined H2 and H3 headings
            - body_text: First 300 words of body content
            - error: Error message if scraping failed
        """
        if not is_valid_url(url):
            return {'error': 'Invalid URL format'}
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            title = clean_text(title_tag.get_text()) if title_tag else ''
            
            # Extract meta description
            meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
            meta_description = ''
            if meta_desc_tag and meta_desc_tag.get('content'):
                meta_description = clean_text(meta_desc_tag['content'])
            
            # Extract H1
            h1_tag = soup.find('h1')
            h1 = clean_text(h1_tag.get_text()) if h1_tag else ''
            
            # Extract H2 and H3 headings
            h2_h3_tags = soup.find_all(['h2', 'h3'])
            h2_h3_texts = [clean_text(tag.get_text()) for tag in h2_h3_tags]
            h2_h3 = ' | '.join(h2_h3_texts[:5])  # Limit to first 5 headings
            
            # Extract body text (first 300 words)
            body_text = self._extract_body_text(soup)
            
            return {
                'title': title,
                'meta_description': meta_description,
                'h1': h1,
                'h2_h3': h2_h3,
                'body_text': body_text,
                'error': ''
            }
            
        except requests.exceptions.Timeout:
            return {'error': f'Request timeout after {self.timeout} seconds'}
        except requests.exceptions.ConnectionError:
            return {'error': 'Failed to connect to the URL'}
        except requests.exceptions.HTTPError as e:
            return {'error': f'HTTP error: {e.response.status_code}'}
        except Exception as e:
            return {'error': f'Scraping failed: {str(e)}'}

    def _extract_body_text(self, soup: BeautifulSoup) -> str:
        """
        Extract body text content, limiting to first 300 words.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            str: Cleaned body text (first 300 words)
        """
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Get text from main content areas
        main_content_selectors = [
            'main', 'article', '.content', '.main', '.post',
            '[role="main"]', '.entry-content', '.post-content'
        ]
        
        body_text = ''
        
        # Try to find main content first
        for selector in main_content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                body_text = clean_text(main_content.get_text())
                break
        
        # Fallback to body if no main content found
        if not body_text:
            body = soup.find('body')
            if body:
                body_text = clean_text(body.get_text())
        
        # Limit to first 300 words
        words = body_text.split()
        if len(words) > 300:
            body_text = ' '.join(words[:300])
        
        return body_text

    def get_page_summary(self, scraped_content: Dict[str, str]) -> str:
        """
        Create a summary of scraped page content.
        
        Args:
            scraped_content: Dictionary containing scraped content
            
        Returns:
            str: Summary of the page content
        """
        if scraped_content.get('error'):
            return f"Error: {scraped_content['error']}"
        
        summary_parts = []
        
        if scraped_content.get('title'):
            summary_parts.append(f"Title: {scraped_content['title']}")
        
        if scraped_content.get('meta_description'):
            summary_parts.append(f"Description: {scraped_content['meta_description']}")
        
        if scraped_content.get('h1'):
            summary_parts.append(f"Main Heading: {scraped_content['h1']}")
        
        if scraped_content.get('h2_h3'):
            summary_parts.append(f"Subheadings: {scraped_content['h2_h3']}")
        
        if scraped_content.get('body_text'):
            # Take first 100 words of body text for summary
            body_words = scraped_content['body_text'].split()[:100]
            summary_parts.append(f"Content: {' '.join(body_words)}")
        
        return ' | '.join(summary_parts)


def scrape_website(url: str) -> Dict[str, str]:
    """
    Convenience function to scrape a website.
    
    Args:
        url: The URL to scrape
        
    Returns:
        Dict containing scraped content
    """
    scraper = WebScraper()
    return scraper.scrape_url(url)