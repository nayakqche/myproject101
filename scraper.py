"""
Web scraping functionality for extracting content from URLs.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
import time
from utils import clean_text, extract_keywords


class WebScraper:
    """
    A web scraper for extracting content from URLs.
    """
    
    def __init__(self, timeout: int = 10):
        """
        Initialize the scraper.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_url(self, url: str) -> Dict[str, any]:
        """
        Scrape content from a URL.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dict: Extracted content with success/error status
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            content = {
                'title': self._extract_title(soup),
                'headings': self._extract_headings(soup),
                'meta_description': self._extract_meta_description(soup),
                'body_text': self._extract_body_text(soup),
                'keywords': []
            }
            
            # Extract keywords from body text
            if content['body_text']:
                content['keywords'] = extract_keywords(content['body_text'])
            
            # Create summary
            summary = self.get_content_summary(content)
            
            return {
                'success': True,
                'title': content['title'],
                'meta_description': content['meta_description'],
                'summary': summary,
                'headings': content['headings'],
                'body_text': content['body_text'],
                'keywords': content['keywords']
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Failed to scrape URL: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error processing content: {str(e)}"
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extract page title.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            str: Page title
        """
        # Try title tag first
        title_tag = soup.find('title')
        if title_tag and title_tag.get_text().strip():
            return clean_text(title_tag.get_text())
        
        # Try h1 as fallback
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.get_text().strip():
            return clean_text(h1_tag.get_text())
        
        return ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract all headings (h1, h2, h3).
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List[str]: List of heading texts
        """
        headings = []
        
        # Find all h1, h2, h3 tags
        for tag in soup.find_all(['h1', 'h2', 'h3']):
            text = tag.get_text().strip()
            if text:
                headings.append(clean_text(text))
        
        return headings[:5]  # Limit to first 5 headings
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """
        Extract meta description.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            str: Meta description
        """
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return clean_text(meta_desc.get('content'))
        
        # Try og:description as fallback
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return clean_text(og_desc.get('content'))
        
        return ""
    
    def _extract_body_text(self, soup: BeautifulSoup) -> str:
        """
        Extract main body text content.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            str: Cleaned body text
        """
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Try to find main content area
        main_content = None
        
        # Look for common main content selectors
        selectors = [
            'main',
            '[role="main"]',
            '.main-content',
            '.content',
            '#content',
            '#main',
            'article'
        ]
        
        for selector in selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return ""
        
        # Extract text
        text = main_content.get_text()
        
        # Clean and truncate
        cleaned_text = clean_text(text, max_length=500)
        
        return cleaned_text
    
    def get_content_summary(self, content: Dict[str, str]) -> str:
        """
        Create a summary of scraped content for copy generation.
        
        Args:
            content: Scraped content dictionary
            
        Returns:
            str: Content summary
        """
        summary_parts = []
        
        if content['title']:
            summary_parts.append(f"Title: {content['title']}")
        
        if content['meta_description']:
            summary_parts.append(f"Description: {content['meta_description']}")
        
        if content['headings']:
            headings_text = " | ".join(content['headings'][:3])
            summary_parts.append(f"Key Headings: {headings_text}")
        
        if content['body_text']:
            # Take first 200 characters of body text
            body_preview = content['body_text'][:200]
            if len(content['body_text']) > 200:
                body_preview += "..."
            summary_parts.append(f"Content: {body_preview}")
        
        return "\n".join(summary_parts)
    
    def extract_value_props(self, content: Dict[str, str]) -> List[str]:
        """
        Extract potential value propositions from content.
        
        Args:
            content: Scraped content dictionary
            
        Returns:
            List[str]: List of value propositions
        """
        value_props = []
        
        # Look for common value proposition indicators
        value_indicators = [
            'benefit', 'advantage', 'feature', 'save', 'fast', 'easy',
            'best', 'top', 'quality', 'premium', 'exclusive', 'limited',
            'guarantee', 'warranty', 'free', 'discount', 'offer', 'deal'
        ]
        
        # Search in title and headings
        search_text = f"{content['title']} {' '.join(content['headings'])}"
        search_text = search_text.lower()
        
        for indicator in value_indicators:
            if indicator in search_text:
                # Find the context around the indicator
                words = search_text.split()
                for i, word in enumerate(words):
                    if indicator in word:
                        # Get surrounding context
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        context = " ".join(words[start:end])
                        value_props.append(context)
                        break
        
        # If no value props found, use keywords
        if not value_props and content['keywords']:
            value_props = content['keywords'][:3]
        
        return value_props[:5]  # Limit to 5 value props