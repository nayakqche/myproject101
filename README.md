# Google Ads Copy Generator

A lightweight, self-hostable web app for generating high-converting Google Ads copy in seconds. Perfect for agencies, solo founders, and freelance copywriters.

## Features

- **URL Scraping**: Extract content from any target URL (title, headings, meta description, body text)
- **Persona-Driven Copy**: Generate ads tailored to specific audience personas
- **Keyword Integration**: Natural keyword incorporation without stuffing
- **Multiple Variants**: 3-5 ad variations per generation
- **One-Click Export**: Download all variants as CSV
- **Fast Response**: ≤500ms for templates, ≤5s with OpenAI GPT-4o

## Setup

### Prerequisites
- Python 3.11+
- pip

### Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

Note: The app works without an OpenAI API key by falling back to templates, but GPT-4o provides better copy quality.

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Enter Target URL**: Paste the URL of the page you want to create ads for
2. **Define Persona**: Describe your target audience (e.g., "budget-conscious first-time homeowner")
3. **Add Keyword**: Enter the primary search term you're bidding on
4. **Generate**: Click to create 3-5 ad variations
5. **Export**: Download all variants as CSV with one click

## Project Structure

```
├── app.py              # Main Streamlit application
├── scraper.py          # URL scraping functionality
├── generator.py        # Ad copy generation logic
├── utils.py           # Utility functions
├── requirements.txt   # Python dependencies
├── .env              # Environment variables (create this)
└── README.md         # This file
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (optional, falls back to templates)

## License

MIT License - Feel free to use, modify, and distribute.

## Error Handling

- **Bad URLs**: Clear error messages for invalid or inaccessible URLs
- **Timeouts**: 10-second timeout for URL scraping
- **Missing API Key**: Automatic fallback to template-based generation
- **Rate Limits**: Graceful handling of OpenAI API limits

## Technical Details

- **Scraping**: BeautifulSoup for HTML parsing
- **NLP**: Simple text processing for value prop extraction
- **Copy Generation**: OpenAI GPT-4o with template fallback
- **Export**: Pandas-powered CSV generation
- **UI**: Streamlit for instant web interface
