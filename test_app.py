"""
Test script for Google Ads Copy Generator components.
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import validate_url, clean_text, extract_keywords
from scraper import WebScraper
from generator import CopyGenerator


def test_utils():
    """Test utility functions."""
    print("Testing utility functions...")
    
    # Test URL validation
    assert validate_url("https://example.com") == True
    assert validate_url("http://test.com/page") == True
    assert validate_url("invalid-url") == False
    
    # Test text cleaning
    cleaned = clean_text("  This is a test   with extra spaces  ")
    assert "  " not in cleaned
    
    # Test keyword extraction
    keywords = extract_keywords("This is a test of keyword extraction functionality")
    assert len(keywords) > 0
    
    print("✅ Utility functions working correctly")


def test_generator():
    """Test copy generator."""
    print("Testing copy generator...")
    
    generator = CopyGenerator()
    
    # Test template generation
    ads = generator.generate_ads(
        content_summary="Test content about home security systems",
        persona="budget-conscious homeowner",
        keyword="security system",
        num_variants=3
    )
    
    assert len(ads) == 3
    for ad in ads:
        assert 'headline1' in ad
        assert 'headline2' in ad
        assert 'description' in ad
        assert len(ad['headline1']) <= 30
        assert len(ad['headline2']) <= 30
        assert len(ad['description']) <= 90
    
    print("✅ Copy generator working correctly")


def test_scraper():
    """Test web scraper with a simple test."""
    print("Testing web scraper...")
    
    scraper = WebScraper()
    
    # Test with a simple HTML string
    test_html = """
    <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
        </head>
        <body>
            <h1>Main Heading</h1>
            <h2>Sub Heading</h2>
            <p>This is some test content for keyword extraction.</p>
        </body>
    </html>
    """
    
    # Mock the scraping process
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(test_html, 'html.parser')
    
    title = scraper._extract_title(soup)
    assert "Test Page" in title
    
    headings = scraper._extract_headings(soup)
    assert len(headings) >= 2
    
    meta_desc = scraper._extract_meta_description(soup)
    assert "Test description" in meta_desc
    
    print("✅ Web scraper working correctly")


def main():
    """Run all tests."""
    print("🧪 Running Google Ads Copy Generator Tests\n")
    
    try:
        test_utils()
        test_generator()
        test_scraper()
        
        print("\n🎉 All tests passed! The application is ready to use.")
        print("\nTo run the app:")
        print("streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()