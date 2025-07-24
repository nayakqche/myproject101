"""
Main Streamlit application for Google Ads copy generator.
"""

import streamlit as st
import pandas as pd
import time
from io import StringIO
from dotenv import load_dotenv

from scraper import scrape_website
from generator import generate_ads
from utils import is_valid_url, validate_ad_copy, get_timestamp

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Google Ads Copy Generator",
    page_icon="📢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #0d5aa7;
    }
    .ad-variant {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }
    .char-count {
        font-size: 0.8rem;
        color: #666;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application function."""
    
    # Header
    st.title("📢 Google Ads Copy Generator")
    st.markdown("Generate high-converting Google Ads copy in seconds. Perfect for agencies, freelancers, and solo founders.")
    
    # Sidebar with instructions
    with st.sidebar:
        st.header("📋 How to Use")
        st.markdown("""
        1. **Enter Target URL** - The page you want to create ads for
        2. **Define Persona** - Your target audience 
        3. **Add Keyword** - Primary search term
        4. **Generate** - Create 3-5 ad variations
        5. **Export** - Download as CSV
        """)
        
        st.header("⚡ Features")
        st.markdown("""
        - URL content scraping
        - AI-powered copy generation
        - Character limit validation
        - One-click CSV export
        - Template fallback
        """)
        
        st.header("🔧 API Status")
        api_key_status = "✅ Connected" if st.session_state.get('openai_available') else "❌ Template Mode"
        st.markdown(f"**OpenAI**: {api_key_status}")
    
    # Main form
    with st.form("ad_generator_form"):
        st.header("🎯 Generate Your Ads")
        
        col1, col2 = st.columns(2)
        
        with col1:
            url = st.text_input(
                "Target URL *",
                placeholder="https://example.com/product-page",
                help="The webpage you want to create ads for"
            )
            
            persona = st.text_area(
                "Target Persona *",
                placeholder="budget-conscious first-time homeowner looking for reliable services",
                help="Describe your ideal customer",
                height=100
            )
        
        with col2:
            keyword = st.text_input(
                "Primary Keyword *",
                placeholder="home security system",
                help="Main search term you're bidding on"
            )
            
            num_variants = st.slider(
                "Number of Variants",
                min_value=3,
                max_value=5,
                value=4,
                help="How many ad variations to generate"
            )
        
        submitted = st.form_submit_button("🚀 Generate Ads", use_container_width=True)
    
    # Process form submission
    if submitted:
        if not url or not persona or not keyword:
            st.error("⚠️ Please fill in all required fields (marked with *)")
            return
        
        if not is_valid_url(url):
            st.error("⚠️ Please enter a valid URL (including http:// or https://)")
            return
        
        # Show processing message
        with st.spinner("🔍 Scraping content and generating ads..."):
            progress_bar = st.progress(0)
            
            # Step 1: Scrape URL
            progress_bar.progress(25)
            scraped_content = scrape_website(url)
            
            # Step 2: Generate ads
            progress_bar.progress(75)
            ads = generate_ads(scraped_content, persona, keyword, num_variants)
            
            progress_bar.progress(100)
        
        # Store results in session state
        st.session_state['generated_ads'] = ads
        st.session_state['input_data'] = {
            'url': url,
            'persona': persona,
            'keyword': keyword
        }
        st.session_state['scraped_content'] = scraped_content
        
        # Clear progress bar
        progress_bar.empty()
        
        # Show success message
        if not scraped_content.get('error'):
            st.success("✅ Ads generated successfully!")
        else:
            st.warning(f"⚠️ URL scraping failed ({scraped_content['error']}), but template ads were generated.")
    
    # Display results if available
    if 'generated_ads' in st.session_state:
        display_results()


def display_results():
    """Display generated ad results with export functionality."""
    
    ads = st.session_state['generated_ads']
    input_data = st.session_state['input_data']
    scraped_content = st.session_state['scraped_content']
    
    st.header("📊 Generated Ad Variants")
    
    # Export button at the top
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("📥 Export to CSV", use_container_width=True):
            csv_data = create_csv_export(ads, input_data)
            timestamp = get_timestamp()
            
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"ads_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("🔄 Generate New", use_container_width=True):
            # Clear session state to start over
            for key in ['generated_ads', 'input_data', 'scraped_content']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Display scraped content summary
    if not scraped_content.get('error'):
        with st.expander("📄 Scraped Content Summary"):
            col1, col2 = st.columns(2)
            
            with col1:
                if scraped_content.get('title'):
                    st.write("**Title:**", scraped_content['title'])
                if scraped_content.get('h1'):
                    st.write("**Main Heading:**", scraped_content['h1'])
            
            with col2:
                if scraped_content.get('meta_description'):
                    st.write("**Meta Description:**", scraped_content['meta_description'])
                if scraped_content.get('h2_h3'):
                    st.write("**Subheadings:**", scraped_content['h2_h3'][:100] + "...")
    
    # Display ads in a nice format
    for i, ad in enumerate(ads, 1):
        validation = validate_ad_copy(ad['headline1'], ad['headline2'], ad['description'])
        
        with st.container():
            st.markdown(f"### Variant {i}")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Display ad content
                st.markdown(f"""
                <div class="ad-variant">
                    <strong>Headline 1:</strong> {ad['headline1']}<br>
                    <span class="char-count">({validation['headline1_length']}/30 chars)</span><br><br>
                    
                    <strong>Headline 2:</strong> {ad['headline2']}<br>
                    <span class="char-count">({validation['headline2_length']}/30 chars)</span><br><br>
                    
                    <strong>Description:</strong> {ad['description']}<br>
                    <span class="char-count">({validation['description_length']}/90 chars)</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Copy buttons and validation status
                if st.button(f"📋 Copy Variant {i}", key=f"copy_{i}"):
                    copy_text = f"H1: {ad['headline1']}\nH2: {ad['headline2']}\nDesc: {ad['description']}"
                    st.code(copy_text, language=None)
                
                # Validation indicators
                status_color = "🟢" if validation['all_valid'] else "🔴"
                st.markdown(f"{status_color} **Valid:** {validation['all_valid']}")
                
                if not validation['headline1_valid']:
                    st.markdown("❗ H1 too long")
                if not validation['headline2_valid']:
                    st.markdown("❗ H2 too long")
                if not validation['description_valid']:
                    st.markdown("❗ Desc too long")
    
    # Display ads in table format
    st.header("📋 Table View")
    df = pd.DataFrame(ads)
    df.index = [f"Variant {i+1}" for i in range(len(df))]
    st.dataframe(df, use_container_width=True)


def create_csv_export(ads: list, input_data: dict) -> str:
    """Create CSV data for export."""
    
    # Prepare data for CSV
    csv_data = []
    
    for i, ad in enumerate(ads, 1):
        csv_data.append({
            'Variant': f"Variant {i}",
            'Headline 1': ad['headline1'],
            'Headline 2': ad['headline2'],
            'Description': ad['description'],
            'H1 Length': len(ad['headline1']),
            'H2 Length': len(ad['headline2']),
            'Desc Length': len(ad['description']),
            'Source URL': input_data['url'],
            'Target Persona': input_data['persona'],
            'Primary Keyword': input_data['keyword'],
            'Generated At': time.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Convert to CSV
    df = pd.DataFrame(csv_data)
    return df.to_csv(index=False)


def check_openai_availability():
    """Check if OpenAI is available and store in session state."""
    import os
    st.session_state['openai_available'] = bool(os.getenv('OPENAI_API_KEY'))


if __name__ == "__main__":
    # Initialize session state
    if 'openai_available' not in st.session_state:
        check_openai_availability()
    
    main()