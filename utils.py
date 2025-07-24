"""
Utility functions for Google Ads copy generator.
"""

import re
import time
from typing import List, Dict, Any
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted.
    
    Args:
        url: The URL string to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    
    return text


def truncate_to_char_limit(text: str, limit: int) -> str:
    """
    Truncate text to character limit, breaking at word boundaries.
    
    Args:
        text: Text to truncate
        limit: Maximum character count
        
    Returns:
        str: Truncated text
    """
    if len(text) <= limit:
        return text
    
    # Find the last space before the limit
    truncated = text[:limit]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        return truncated[:last_space]
    else:
        return truncated


def extract_keywords_from_text(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract potential keywords from text using simple frequency analysis.
    
    Args:
        text: Text to analyze
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List[str]: List of extracted keywords
    """
    if not text:
        return []
    
    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Common stop words to exclude
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
        'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who',
        'boy', 'did', 'she', 'use', 'your', 'they', 'from', 'know', 'want',
        'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here',
        'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than',
        'them', 'well', 'will', 'with', 'have', 'this', 'that', 'what', 'were'
    }
    
    # Filter and count words
    word_freq = {}
    for word in words:
        if word not in stop_words and len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]


def extract_value_props(text: str) -> List[str]:
    """
    Extract potential value propositions from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List[str]: List of potential value propositions
    """
    if not text:
        return []
    
    value_prop_patterns = [
        r'save \$?\d+',
        r'free \w+',
        r'guaranteed \w+',
        r'instant \w+',
        r'24/7 \w+',
        r'expert \w+',
        r'professional \w+',
        r'certified \w+',
        r'trusted \w+',
        r'award[- ]winning',
        r'best \w+',
        r'top[- ]rated',
        r'fastest \w+',
        r'easiest \w+',
        r'simple \w+',
        r'affordable \w+',
        r'budget[- ]friendly',
        r'no[- ]cost \w+',
        r'money[- ]back \w+',
        r'\d+[%] off',
        r'\d+[%] discount',
        r'\d+ years? experience',
        r'since \d{4}',
    ]
    
    value_props = []
    text_lower = text.lower()
    
    for pattern in value_prop_patterns:
        matches = re.findall(pattern, text_lower)
        value_props.extend(matches)
    
    return list(set(value_props))  # Remove duplicates


def get_timestamp() -> str:
    """
    Get current timestamp for file naming.
    
    Returns:
        str: Formatted timestamp
    """
    return time.strftime("%Y%m%d_%H%M%S")


def validate_ad_copy(headline1: str, headline2: str, description: str) -> Dict[str, Any]:
    """
    Validate Google Ads copy against character limits.
    
    Args:
        headline1: First headline
        headline2: Second headline  
        description: Ad description
        
    Returns:
        Dict containing validation results
    """
    return {
        'headline1_valid': len(headline1) <= 30,
        'headline1_length': len(headline1),
        'headline2_valid': len(headline2) <= 30,
        'headline2_length': len(headline2),
        'description_valid': len(description) <= 90,
        'description_length': len(description),
        'all_valid': len(headline1) <= 30 and len(headline2) <= 30 and len(description) <= 90
    }