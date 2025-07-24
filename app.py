"""
Google Ads Copy Generator - Main Streamlit Application
"""

import streamlit as st
import time
from typing import List, Dict
import io

from scraper import WebScraper
from generator import CopyGenerator
from utils import (
    validate_url, 
    export_to_csv, 
    get_openai_api_key,
    validate_google_ads_limits
)


def main():
    """
    Main Streamlit application.
    """
    # Page configuration
    st.set_page_config(
        page_title="Google Ads Copy Generator",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">📝 Google Ads Copy Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Generate high-converting Google Ads copy in seconds</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key status
        api_key = get_openai_api_key()
        if api_key:
            st.success("✅ OpenAI API configured")
        else:
            st.warning("⚠️ No OpenAI API key found - using template generation")
            st.info("Add OPENAI_API_KEY to .env for AI-powered copy")
        
        st.divider()
        
        # Number of variants
        num_variants = st.slider(
            "Number of Ad Variants",
            min_value=3,
            max_value=10,
            value=5,
            help="How many different ad variations to generate"
        )
        
        # Advanced options
        with st.expander("Advanced Options"):
            st.checkbox("Show content analysis", value=True, key="show_analysis")
            st.checkbox("Validate character limits", value=True, key="validate_limits")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎯 Input Parameters")
        
        # URL input
        target_url = st.text_input(
            "Target URL",
            placeholder="https://example.com/product-page",
            help="The page to scrape for context and content"
        )
        
        # Persona input
        persona = st.text_input(
            "Target Persona",
            placeholder="budget-conscious first-time homeowner",
            help="Describe your target audience"
        )
        
        # Keyword input
        keyword = st.text_input(
            "Primary Keyword",
            placeholder="home security system",
            help="The main search term you're bidding on"
        )
        
        # Generate button
        generate_button = st.button(
            "🚀 Generate Ads",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        st.header("📊 Status")
        
        # Status indicators
        if target_url:
            if validate_url(target_url):
                st.success("✅ Valid URL")
            else:
                st.error("❌ Invalid URL format")
        
        if persona:
            st.success(f"✅ Persona: {persona}")
        
        if keyword:
            st.success(f"✅ Keyword: {keyword}")
    
    # Processing and results
    if generate_button:
        if not all([target_url, persona, keyword]):
            st.error("Please fill in all required fields")
            return
        
        if not validate_url(target_url):
            st.error("Please enter a valid URL")
            return
        
        # Initialize components
        scraper = WebScraper()
        generator = CopyGenerator()
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Scrape URL
            status_text.text("🔍 Scraping target URL...")
            progress_bar.progress(20)
            
            scraped_content = scraper.scrape_url(target_url)
            content_summary = scraper.get_content_summary(scraped_content)
            
            # Show content analysis if enabled
            if st.session_state.get("show_analysis", True):
                with st.expander("📋 Content Analysis", expanded=True):
                    st.write("**Page Title:**", scraped_content.get('title', 'N/A'))
                    st.write("**Meta Description:**", scraped_content.get('meta_description', 'N/A'))
                    st.write("**Key Headings:**", " | ".join(scraped_content.get('headings', [])[:3]))
                    st.write("**Extracted Keywords:**", ", ".join(scraped_content.get('keywords', [])[:5]))
            
            progress_bar.progress(50)
            
            # Step 2: Generate ads
            status_text.text("✍️ Generating ad copy...")
            progress_bar.progress(70)
            
            ads = generator.generate_ads(content_summary, persona, keyword, num_variants)
            ads = generator.validate_ads(ads)
            
            progress_bar.progress(90)
            
            # Step 3: Display results
            status_text.text("✅ Generation complete!")
            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            st.header("📄 Generated Ads")
            
            if not ads:
                st.error("No ads were generated. Please try again.")
                return
            
            # Create results table
            for i, ad in enumerate(ads, 1):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Ad {i}**")
                        
                        # Character count validation
                        if st.session_state.get("validate_limits", True):
                            limits = validate_google_ads_limits(
                                ad['headline1'], 
                                ad['headline2'], 
                                ad['description']
                            )
                            
                            headline1_color = "✅" if limits['headline1_valid'] else "⚠️"
                            headline2_color = "✅" if limits['headline2_valid'] else "⚠️"
                            desc_color = "✅" if limits['description_valid'] else "⚠️"
                        else:
                            headline1_color = headline2_color = desc_color = "📝"
                        
                        st.write(f"{headline1_color} **Headline 1:** {ad['headline1']} ({len(ad['headline1'])}/30)")
                        st.write(f"{headline2_color} **Headline 2:** {ad['headline2']} ({len(ad['headline2'])}/30)")
                        st.write(f"{desc_color} **Description:** {ad['description']} ({len(ad['description'])}/90)")
                    
                    with col2:
                        # Copy button
                        if st.button(f"📋 Copy Ad {i}", key=f"copy_{i}"):
                            ad_text = f"Headline 1: {ad['headline1']}\nHeadline 2: {ad['headline2']}\nDescription: {ad['description']}"
                            st.write("```")
                            st.code(ad_text)
                            st.write("```")
                    
                    st.divider()
            
            # Export functionality
            st.header("📤 Export Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Export to CSV", type="secondary", use_container_width=True):
                    filename, csv_data = export_to_csv(ads)
                    
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("📋 Copy All Ads", type="secondary", use_container_width=True):
                    all_ads_text = ""
                    for i, ad in enumerate(ads, 1):
                        all_ads_text += f"Ad {i}:\n"
                        all_ads_text += f"Headline 1: {ad['headline1']}\n"
                        all_ads_text += f"Headline 2: {ad['headline2']}\n"
                        all_ads_text += f"Description: {ad['description']}\n\n"
                    
                    st.text_area("All Ads:", all_ads_text, height=200)
            
            # Success message
            st.success(f"✅ Successfully generated {len(ads)} ad variants!")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Try checking the URL or adjusting your inputs")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        Built with ❤️ for agencies, solo founders, and freelance copywriters
        </div>
        """, 
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()