"""
Utility functions for the Google Ads Copy Generator.
"""

import re
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def validate_url(url: str) -> bool:
    """
    Validate if the provided URL is properly formatted.
    
    Args:
        url: The URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def clean_text(text: str, max_length: int = 300) -> str:
    """
    Clean and truncate text for processing.
    
    Args:
        text: Raw text to clean
        max_length: Maximum length of cleaned text
        
    Returns:
        str: Cleaned and truncated text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation
    cleaned = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', cleaned)
    
    # Truncate to max_length
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rsplit(' ', 1)[0] + "..."
    
    return cleaned


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    Extract potential keywords from text using simple frequency analysis.
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List[str]: List of extracted keywords
    """
    if not text:
        return []
    
    # Convert to lowercase and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
        'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
    }
    
    # Filter out stop words and short words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count frequency
    word_count = {}
    for word in keywords:
        word_count[word] = word_count.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_keywords = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_keywords[:max_keywords]]


def truncate_for_google_ads(text: str, max_length: int) -> str:
    """
    Truncate text to fit Google Ads character limits.
    
    Args:
        text: Text to truncate
        max_length: Maximum character length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    # Try to truncate at a word boundary
    truncated = text[:max_length].rsplit(' ', 1)[0]
    
    # If still too long, truncate at character level
    if len(truncated) > max_length:
        truncated = text[:max_length-3] + "..."
    
    return truncated


def create_csv_filename() -> str:
    """
    Create a timestamped filename for CSV export.
    
    Returns:
        str: Filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"ads_{timestamp}.csv"


def export_to_csv(ads_data: List[Dict[str, str]]) -> Tuple[str, bytes]:
    """
    Export ads data to CSV format.
    
    Args:
        ads_data: List of dictionaries containing ad data
        
    Returns:
        Tuple[str, bytes]: Filename and CSV data as bytes
    """
    df = pd.DataFrame(ads_data)
    filename = create_csv_filename()
    csv_data = df.to_csv(index=False).encode('utf-8')
    return filename, csv_data


def get_openai_api_key() -> Optional[str]:
    """
    Get OpenAI API key from environment variables.
    
    Returns:
        Optional[str]: API key if available, None otherwise
    """
    return os.getenv('OPENAI_API_KEY')


def get_openai_model() -> str:
    """
    Get OpenAI model name from environment variables.
    
    Returns:
        str: Model name (default: gpt-4o-mini)
    """
    return os.getenv('OPENAI_MODEL', 'gpt-4o-mini')


def format_persona_prompt(persona: str) -> str:
    """
    Format persona text for use in prompts.
    
    Args:
        persona: Raw persona description
        
    Returns:
        str: Formatted persona prompt
    """
    if not persona:
        return "general audience"
    
    # Clean and capitalize
    formatted = persona.strip().lower()
    if formatted.endswith('.'):
        formatted = formatted[:-1]
    
    return formatted


def validate_google_ads_limits(headline1: str, headline2: str, description: str) -> Dict[str, bool]:
    """
    Validate Google Ads character limits.
    
    Args:
        headline1: First headline
        headline2: Second headline
        description: Ad description
        
    Returns:
        Dict[str, bool]: Validation results for each field
    """
    return {
        'headline1_valid': len(headline1) <= 30,
        'headline2_valid': len(headline2) <= 30,
        'description_valid': len(description) <= 90
    }