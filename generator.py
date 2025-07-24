"""
Google Ads copy generation functionality.
"""

import os
import random
from typing import List, Dict, Optional
from openai import OpenAI
from utils import truncate_to_char_limit, extract_value_props, extract_keywords_from_text


class AdCopyGenerator:
    """Generator for Google Ads copy with OpenAI and template fallback."""
    
    def __init__(self):
        """Initialize the ad copy generator."""
        self.openai_client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if self.api_key:
            try:
                self.openai_client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")
                self.openai_client = None

    def generate_copy(
        self,
        scraped_content: Dict[str, str],
        persona: str,
        keyword: str,
        num_variants: int = 4
    ) -> List[Dict[str, str]]:
        """
        Generate Google Ads copy variants.
        
        Args:
            scraped_content: Content scraped from target URL
            persona: Target audience description
            keyword: Primary keyword to target
            num_variants: Number of ad variants to generate
            
        Returns:
            List of ad copy variants, each containing headline1, headline2, description
        """
        if scraped_content.get('error'):
            return self._generate_error_fallback(scraped_content['error'])
        
        # Try OpenAI first, fall back to templates
        if self.openai_client:
            try:
                return self._generate_with_openai(scraped_content, persona, keyword, num_variants)
            except Exception as e:
                print(f"OpenAI generation failed: {e}")
                return self._generate_with_templates(scraped_content, persona, keyword, num_variants)
        else:
            return self._generate_with_templates(scraped_content, persona, keyword, num_variants)

    def _generate_with_openai(
        self,
        scraped_content: Dict[str, str],
        persona: str,
        keyword: str,
        num_variants: int
    ) -> List[Dict[str, str]]:
        """Generate ads using OpenAI GPT-4o."""
        
        # Prepare context for the AI
        context = self._build_context(scraped_content, persona, keyword)
        
        prompt = f"""
You are an expert direct-response copywriter specializing in Google Ads. Generate {num_variants} high-converting Google Ads variants based on this context:

CONTEXT: {context}

REQUIREMENTS:
- Each ad needs exactly 2 headlines (max 30 characters each) and 1 description (max 90 characters)
- Include the keyword "{keyword}" naturally (don't stuff)
- Target persona: {persona}
- Focus on pain points, benefits, and urgency
- Use proven direct-response techniques

FORMAT YOUR RESPONSE AS JSON:
[
  {{
    "headline1": "Your first headline",
    "headline2": "Your second headline", 
    "description": "Your compelling description with clear CTA"
  }}
]

Remember: Character limits are STRICT. Headlines: 30 chars max. Description: 90 chars max.
"""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=1000
        )
        
        # Parse the JSON response
        import json
        try:
            ads = json.loads(response.choices[0].message.content)
            
            # Validate and truncate if needed
            validated_ads = []
            for ad in ads:
                validated_ads.append({
                    'headline1': truncate_to_char_limit(ad.get('headline1', ''), 30),
                    'headline2': truncate_to_char_limit(ad.get('headline2', ''), 30),
                    'description': truncate_to_char_limit(ad.get('description', ''), 90)
                })
            
            return validated_ads[:num_variants]
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return self._generate_with_templates(scraped_content, persona, keyword, num_variants)

    def _generate_with_templates(
        self,
        scraped_content: Dict[str, str],
        persona: str,
        keyword: str,
        num_variants: int
    ) -> List[Dict[str, str]]:
        """Generate ads using predefined templates."""
        
        # Extract key information
        title = scraped_content.get('title', '')
        value_props = extract_value_props(scraped_content.get('body_text', ''))
        keywords_found = extract_keywords_from_text(scraped_content.get('body_text', ''))
        
        # Template patterns for headlines
        headline_templates = [
            f"{keyword.title()} Solutions",
            f"Best {keyword.title()}",
            f"{keyword.title()} Experts",
            f"Top {keyword.title()}",
            f"{keyword.title()} Service",
            f"Get {keyword.title()}",
            f"{keyword.title()} Help",
            f"Pro {keyword.title()}",
            f"{keyword.title()} Fast",
            f"Quality {keyword.title()}"
        ]
        
        # Template patterns for descriptions
        description_templates = [
            f"Professional {keyword} services for {persona}. Get started today!",
            f"Expert {keyword} solutions. Perfect for {persona}. Contact us now!",
            f"Trusted {keyword} services. Designed for {persona}. Learn more!",
            f"Quality {keyword} at great prices. Ideal for {persona}. Call today!",
            f"Fast, reliable {keyword} services. Built for {persona}. Get quote!"
        ]
        
        # Add value prop variations if found
        if value_props:
            for prop in value_props[:3]:
                description_templates.append(f"{prop.title()} {keyword} for {persona}. Start now!")
        
        # Generate variants
        ads = []
        used_combinations = set()
        
        for i in range(num_variants):
            # Ensure unique combinations
            attempts = 0
            while attempts < 20:  # Prevent infinite loop
                h1 = random.choice(headline_templates)
                h2 = random.choice([t for t in headline_templates if t != h1])
                desc = random.choice(description_templates)
                
                combination = (h1, h2, desc)
                if combination not in used_combinations:
                    used_combinations.add(combination)
                    break
                attempts += 1
            
            # Truncate to limits
            ads.append({
                'headline1': truncate_to_char_limit(h1, 30),
                'headline2': truncate_to_char_limit(h2, 30),
                'description': truncate_to_char_limit(desc, 90)
            })
        
        return ads

    def _generate_error_fallback(self, error_message: str) -> List[Dict[str, str]]:
        """Generate fallback ads when scraping fails."""
        return [{
            'headline1': 'Quality Service',
            'headline2': 'Get Started Today',
            'description': f'Professional solutions for your needs. Contact us! (Note: {error_message})'
        }]

    def _build_context(self, scraped_content: Dict[str, str], persona: str, keyword: str) -> str:
        """Build context string for AI generation."""
        context_parts = []
        
        if scraped_content.get('title'):
            context_parts.append(f"Page Title: {scraped_content['title']}")
        
        if scraped_content.get('meta_description'):
            context_parts.append(f"Description: {scraped_content['meta_description']}")
        
        if scraped_content.get('h1'):
            context_parts.append(f"Main Heading: {scraped_content['h1']}")
        
        if scraped_content.get('body_text'):
            # Use first 200 words for context
            body_words = scraped_content['body_text'].split()[:200]
            context_parts.append(f"Content: {' '.join(body_words)}")
        
        context_parts.append(f"Target Persona: {persona}")
        context_parts.append(f"Primary Keyword: {keyword}")
        
        return ' | '.join(context_parts)


def generate_ads(
    scraped_content: Dict[str, str],
    persona: str,
    keyword: str,
    num_variants: int = 4
) -> List[Dict[str, str]]:
    """
    Convenience function to generate ad copy.
    
    Args:
        scraped_content: Content scraped from target URL
        persona: Target audience description
        keyword: Primary keyword to target
        num_variants: Number of ad variants to generate
        
    Returns:
        List of ad copy variants
    """
    generator = AdCopyGenerator()
    return generator.generate_copy(scraped_content, persona, keyword, num_variants)