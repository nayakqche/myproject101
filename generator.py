"""
Copy generation functionality for Google Ads.
"""

import openai
from typing import List, Dict, Optional
import random
from utils import (
    truncate_for_google_ads, 
    get_openai_api_key, 
    get_openai_model,
    format_persona_prompt
)


class CopyGenerator:
    """
    Generates Google Ads copy using OpenAI API or template-based approach.
    """
    
    def __init__(self):
        """
        Initialize the copy generator.
        """
        self.api_key = get_openai_api_key()
        self.model = get_openai_model()
        
        if self.api_key:
            openai.api_key = self.api_key
    
    def generate_ads(self, 
                    content_summary: str, 
                    persona: str, 
                    keyword: str, 
                    num_variants: int = 5) -> List[Dict[str, str]]:
        """
        Generate Google Ads copy variants.
        
        Args:
            content_summary: Summary of scraped content
            persona: Target audience persona
            keyword: Primary keyword to target
            num_variants: Number of ad variants to generate
            
        Returns:
            List[Dict[str, str]]: List of ad variants with headlines and descriptions
        """
        if self.api_key:
            return self._generate_with_openai(content_summary, persona, keyword, num_variants)
        else:
            return self._generate_with_templates(content_summary, persona, keyword, num_variants)
    
    def _generate_with_openai(self, 
                             content_summary: str, 
                             persona: str, 
                             keyword: str, 
                             num_variants: int) -> List[Dict[str, str]]:
        """
        Generate ads using OpenAI API.
        
        Args:
            content_summary: Summary of scraped content
            persona: Target audience persona
            keyword: Primary keyword to target
            num_variants: Number of ad variants to generate
            
        Returns:
            List[Dict[str, str]]: List of ad variants
        """
        try:
            prompt = self._create_openai_prompt(content_summary, persona, keyword, num_variants)
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Google Ads copywriter who creates high-converting ad copy."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Parse the response
            ads_text = response.choices[0].message.content
            return self._parse_openai_response(ads_text, num_variants)
            
        except Exception as e:
            # Fallback to templates if OpenAI fails
            return self._generate_with_templates(content_summary, persona, keyword, num_variants)
    
    def _create_openai_prompt(self, 
                             content_summary: str, 
                             persona: str, 
                             keyword: str, 
                             num_variants: int) -> str:
        """
        Create prompt for OpenAI API.
        
        Args:
            content_summary: Summary of scraped content
            persona: Target audience persona
            keyword: Primary keyword to target
            num_variants: Number of ad variants to generate
            
        Returns:
            str: Formatted prompt
        """
        formatted_persona = format_persona_prompt(persona)
        
        prompt = f"""
Create {num_variants} high-converting Google Ads variants for the following:

CONTENT SUMMARY:
{content_summary}

TARGET PERSONA: {formatted_persona}
PRIMARY KEYWORD: {keyword}

Requirements:
- Headline 1: Maximum 30 characters
- Headline 2: Maximum 30 characters  
- Description: Maximum 90 characters
- Naturally incorporate the keyword
- Address the persona's pain points
- Focus on value propositions and benefits
- Use action-oriented language
- Include a clear call-to-action

Format each ad as:
Ad 1:
Headline 1: [text]
Headline 2: [text]
Description: [text]

Ad 2:
Headline 1: [text]
Headline 2: [text]
Description: [text]

...and so on for all {num_variants} ads.
"""
        return prompt
    
    def _parse_openai_response(self, response_text: str, expected_variants: int) -> List[Dict[str, str]]:
        """
        Parse OpenAI response into structured ad data.
        
        Args:
            response_text: Raw response from OpenAI
            expected_variants: Expected number of variants
            
        Returns:
            List[Dict[str, str]]: Parsed ad variants
        """
        ads = []
        lines = response_text.split('\n')
        
        current_ad = {}
        ad_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.lower().startswith('ad ') and ':' in line:
                if current_ad and len(current_ad) == 3:
                    ads.append(current_ad)
                    current_ad = {}
                ad_count += 1
                
            elif 'headline 1:' in line.lower():
                headline1 = line.split(':', 1)[1].strip()
                current_ad['headline1'] = truncate_for_google_ads(headline1, 30)
                
            elif 'headline 2:' in line.lower():
                headline2 = line.split(':', 1)[1].strip()
                current_ad['headline2'] = truncate_for_google_ads(headline2, 30)
                
            elif 'description:' in line.lower():
                description = line.split(':', 1)[1].strip()
                current_ad['description'] = truncate_for_google_ads(description, 90)
        
        # Add the last ad if complete
        if current_ad and len(current_ad) == 3:
            ads.append(current_ad)
        
        # If parsing failed, fallback to templates
        if len(ads) < expected_variants:
            return self._generate_with_templates("", "", "", expected_variants)
        
        return ads[:expected_variants]
    
    def _generate_with_templates(self, 
                               content_summary: str, 
                               persona: str, 
                               keyword: str, 
                               num_variants: int) -> List[Dict[str, str]]:
        """
        Generate ads using template-based approach.
        
        Args:
            content_summary: Summary of scraped content
            persona: Target audience persona
            keyword: Primary keyword to target
            num_variants: Number of ad variants to generate
            
        Returns:
            List[Dict[str, str]]: List of ad variants
        """
        # Extract key terms from content
        content_words = content_summary.lower().split()
        value_words = [word for word in content_words if len(word) > 3][:10]
        
        # Template patterns
        headline_templates = [
            f"Best {keyword} Deals",
            f"Top {keyword} Options", 
            f"Quality {keyword} Here",
            f"Find Your {keyword}",
            f"Premium {keyword} Now",
            f"Save on {keyword}",
            f"Expert {keyword} Guide",
            f"Trusted {keyword} Source"
        ]
        
        description_templates = [
            f"Get the best {keyword} deals. Fast shipping & expert support. Shop now!",
            f"Find quality {keyword} options. Compare prices & save big today!",
            f"Premium {keyword} selection. Free shipping & 30-day returns. Buy now!",
            f"Expert {keyword} advice. Best prices guaranteed. Limited time offer!",
            f"Trusted {keyword} source. Fast delivery & customer satisfaction. Order today!"
        ]
        
        ads = []
        used_combinations = set()
        
        for i in range(num_variants):
            # Generate unique combination
            attempts = 0
            while attempts < 20:
                headline1 = random.choice(headline_templates)
                headline2 = random.choice([
                    "Free Shipping",
                    "Best Prices", 
                    "Expert Support",
                    "Quality Guaranteed",
                    "Fast Delivery",
                    "Save Big Today",
                    "Limited Time",
                    "Trusted Source"
                ])
                description = random.choice(description_templates)
                
                combination = (headline1, headline2, description)
                if combination not in used_combinations:
                    used_combinations.add(combination)
                    break
                attempts += 1
            
            # Ensure keyword is included
            if keyword.lower() not in headline1.lower():
                headline1 = f"Best {keyword} Deals"
            
            ads.append({
                'headline1': truncate_for_google_ads(headline1, 30),
                'headline2': truncate_for_google_ads(headline2, 30),
                'description': truncate_for_google_ads(description, 90)
            })
        
        return ads
    
    def validate_ads(self, ads: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Validate and clean generated ads.
        
        Args:
            ads: List of ad variants
            
        Returns:
            List[Dict[str, str]]: Validated ads
        """
        validated_ads = []
        
        for ad in ads:
            # Ensure all required fields exist
            if 'headline1' not in ad or 'headline2' not in ad or 'description' not in ad:
                continue
                
            # Validate character limits
            if (len(ad['headline1']) <= 30 and 
                len(ad['headline2']) <= 30 and 
                len(ad['description']) <= 90):
                validated_ads.append(ad)
        
        return validated_ads