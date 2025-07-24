# Google Ads Copy Generator

A micro web app that generates high-converting Google Ads copy by scraping target URLs and understanding personas. Built for agencies, solo founders, and freelance copywriters who need quick, effective ad copy.

## Features

- **Smart URL Scraping**: Extracts title, headings, meta descriptions, and key content
- **Persona-Driven Copy**: Generates copy tailored to specific audience personas
- **Keyword Integration**: Naturally weaves target keywords into headlines and descriptions
- **Multiple Variants**: Produces 3-5 different ad variations
- **One-Click Export**: Download all variants as CSV for easy import into Google Ads
- **Template Fallback**: Works without OpenAI API key using smart templates

## Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd google-ads-copy-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key if you have one
```

4. Run the app:
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Note**: The app works without an API key using template-based generation, but OpenAI integration provides more sophisticated copy.

## Usage

1. **Enter Target URL**: The page you want to scrape for context (product page, article, etc.)
2. **Define Persona**: Describe your target audience (e.g., "budget-conscious first-time homeowner")
3. **Add Keyword**: The primary search term you're bidding on
4. **Generate**: Click to create 3-5 ad variants
5. **Export**: Download results as CSV for Google Ads import

## Output Format

Each generated ad includes:
- **Headline 1** (≤30 characters)
- **Headline 2** (≤30 characters) 
- **Description** (≤90 characters)

## Architecture

- `app.py`: Main Streamlit application
- `scraper.py`: URL scraping and content extraction
- `generator.py`: Copy generation logic (OpenAI + templates)
- `utils.py`: Helper functions and utilities

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and feature requests, please open an issue on GitHub.
