#!/usr/bin/env python3
"""
Demo script for Google Ads Copy Generator.
Shows how to use the components programmatically.
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import WebScraper
from generator import CopyGenerator
from utils import export_to_csv


def demo():
    """Run a demo of the Google Ads Copy Generator."""
    print("🎯 Google Ads Copy Generator Demo")
    print("=" * 50)
    
    # Initialize components
    scraper = WebScraper()
    generator = CopyGenerator()
    
    # Demo parameters
    target_url = "https://example.com"  # Replace with actual URL
    persona = "budget-conscious first-time homeowner"
    keyword = "home insurance"
    
    print(f"📄 Target URL: {target_url}")
    print(f"👤 Persona: {persona}")
    print(f"🔑 Keyword: {keyword}")
    print()
    
    try:
        # Step 1: Scrape content
        print("🔍 Scraping content...")
        content = scraper.scrape_url(target_url)
        
        if content['success']:
            print(f"✅ Successfully scraped content")
            print(f"📝 Title: {content['title'][:50]}...")
            print(f"📄 Meta Description: {content['meta_description'][:50]}...")
            print()
            
            # Step 2: Generate copy
            print("✍️ Generating Google Ads copy...")
            ads = generator.generate_ads(
                content_summary=content['summary'],
                persona=persona,
                keyword=keyword,
                num_variants=3
            )
            
            if ads:
                print(f"✅ Generated {len(ads)} ad variants")
                print()
                
                # Display results
                for i, ad in enumerate(ads, 1):
                    print(f"📋 Ad Variant {i}:")
                    print(f"   Headline 1: {ad['headline1']}")
                    print(f"   Headline 2: {ad['headline2']}")
                    print(f"   Description: {ad['description']}")
                    print()
                
                # Export to CSV
                print("💾 Exporting to CSV...")
                filename, csv_data = export_to_csv(ads)
                print(f"✅ Exported to: {filename}")
                
            else:
                print("❌ Failed to generate ads")
                
        else:
            print(f"❌ Failed to scrape content: {content['error']}")
            
    except Exception as e:
        print(f"❌ Error during demo: {e}")


if __name__ == "__main__":
    demo()