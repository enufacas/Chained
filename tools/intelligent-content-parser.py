#!/usr/bin/env python3
"""
Intelligent Content Parser

Filters out ads, sponsor content, and malformed text from learning sources.
Cleans up emojis, normalizes text, and validates content quality.

Part of the Chained autonomous AI ecosystem.
Created by Create Guru - inspired by Nikola Tesla's vision for elegant systems.
"""

import re
import json
import unicodedata
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ContentQuality:
    """Represents the quality assessment of content"""
    is_valid: bool
    confidence: float  # 0.0 to 1.0
    issues: List[str]
    cleaned_content: Optional[str] = None


class IntelligentContentParser:
    """
    Intelligent parser that filters ads and cleans content from learning sources.
    
    Features:
    - Detects and removes sponsor/ad content
    - Cleans malformed emojis and special characters
    - Normalizes text for readability
    - Validates content quality
    - Adds metadata about content confidence
    """
    
    # Patterns that indicate sponsor/ad content
    AD_PATTERNS = [
        # Explicit sponsor markers
        r'\(sponsor\)',
        r'\(sponsored\)',
        r'sponsor:',
        r'sponsored by',
        r'brought to you by',
        
        # Call-to-action patterns
        r'sign up now',
        r'register now',
        r'join\s+(us\s+)?(for|today|now)',
        r'download\s+(now|today|for free)',
        r'get\s+\$?\d+.*credits?',
        r'claim your benefits',
        r'start building',
        r'learn more\s*>',
        r'schedule a demo',
        r'register for free',
        
        # Common sponsor content patterns
        r'coffee chat:',
        r'developer coffee chat',
        r'goodbye (low|high).*coverage',
        r'beyond commands:',
        r'get \$\d+.*when you upgrade',
        r'the platform powering',
        r'considering a.*membership',
        r'modern apps run on',
        r'trusted by.*and.*,',
        
        # Promotional language
        r'no slides!',
        r'unlimited parallel',
        r'zero flakes, guaranteed',
        r'your first.*free',
        r'\d+x more.*cases',
        r'\d+% faster.*cycles',
        r'access the full.*library',
    ]
    
    # Patterns for promotional sections
    PROMO_SECTION_PATTERNS = [
        r'^[A-Z].*\(Sponsor\)$',  # Titles ending with (Sponsor)
        r'^Get \$\d+',  # Titles starting with "Get $X"
        r'^Goodbye',  # "Goodbye X" pattern
        r'^\d+ prompts for',  # "X prompts for Y"
    ]
    
    # Known sponsor product names
    SPONSOR_PRODUCTS = [
        'supabase', 'orkes', 'conductor', 'qa wolf', 'warp', 'workos',
        'drata', 'notion agents', 'google developer premium', 'gemini',
    ]
    
    def __init__(self):
        """Initialize the parser with compiled patterns for efficiency"""
        self.ad_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.AD_PATTERNS]
        self.promo_section_compiled = [re.compile(pattern) for pattern in self.PROMO_SECTION_PATTERNS]
        self.sponsor_products_compiled = [re.compile(r'\b' + re.escape(product) + r'\b', re.IGNORECASE) 
                                         for product in self.SPONSOR_PRODUCTS]
    
    def clean_emoji(self, text: str) -> str:
        """
        Clean malformed emojis and special characters.
        
        Converts Unicode emoji representations to their actual symbols or removes them if malformed.
        """
        # Replace common emoji unicode patterns that appear as \udXXX
        emoji_map = {
            '\ud83d\udcb0': '💰',
            '\ud83d\ude80': '🚀',
            '\ud83d\udc68\u200d\ud83d\udcbb': '👨‍💻',
            '\ud83d\udcf1': '📱',
            '\ud83d\udef0\ufe0f': '🛰️',
            '\ud83d\udcbc': '💼',
            '\u26a1': '⚡',
            '\ud83d\udcac': '💬',
            '\ud83c\udf0d': '🌍',
            '\ud83d\udde3': '🗣️',
            '\ud83e\udd16': '🤖',
        }
        
        for unicode_seq, emoji in emoji_map.items():
            text = text.replace(unicode_seq, emoji)
        
        # Remove any remaining malformed unicode sequences
        # This regex catches patterns like \udXXX that weren't mapped
        text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKC', text)
        
        return text
    
    def is_sponsor_content(self, text: str) -> Tuple[bool, List[str]]:
        """
        Detect if text contains sponsor/ad content.
        
        Returns:
            Tuple of (is_sponsor, reasons)
        """
        reasons = []
        
        # Check for ad patterns
        for pattern in self.ad_patterns_compiled:
            if pattern.search(text):
                reasons.append(f"Matches ad pattern: {pattern.pattern}")
        
        # Check for sponsor products
        for product_pattern in self.sponsor_products_compiled:
            if product_pattern.search(text):
                reasons.append(f"Mentions sponsor product: {product_pattern.pattern}")
        
        # High density of promotional language
        promotional_words = ['free', 'now', 'today', 'join', 'get', 'claim', 'unlimited', 'guaranteed']
        promo_count = sum(1 for word in promotional_words if word in text.lower())
        if promo_count >= 4:
            reasons.append(f"High promotional word density: {promo_count} words")
        
        return len(reasons) > 0, reasons
    
    def is_promo_section_title(self, title: str) -> bool:
        """Check if a title indicates a promotional section"""
        for pattern in self.promo_section_compiled:
            if pattern.match(title):
                return True
        return False
    
    def extract_clean_content(self, content: str) -> str:
        """
        Extract clean content by removing sponsor sections.
        
        Splits content into paragraphs and removes those that are promotional.
        """
        if not content:
            return content
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Filter out sponsor paragraphs
        clean_paragraphs = []
        for para in paragraphs:
            is_sponsor, _ = self.is_sponsor_content(para)
            
            # Additional check: if paragraph has high caps density, might be promotional
            if len(para) > 30 and (sum(1 for c in para if c.isupper()) / max(len(para), 1)) > 0.3:
                is_sponsor = True
            
            if not is_sponsor:
                clean_paragraphs.append(para)
        
        return '\n\n'.join(clean_paragraphs)
    
    def clean_title(self, title: str) -> str:
        """Clean up title by removing emojis and normalizing"""
        # Clean emojis
        title = self.clean_emoji(title)
        
        # Remove excessive whitespace
        title = re.sub(r'\s+', ' ', title)
        
        # Remove trailing/leading emojis and special chars
        title = re.sub(r'^[\W\s]+|[\W\s]+$', '', title)
        
        return title.strip()
    
    def assess_content_quality(self, learning: Dict[str, Any]) -> ContentQuality:
        """
        Assess the quality of a learning entry.
        
        Returns a ContentQuality object with validation results.
        """
        issues = []
        
        # Check if title exists and is valid
        title = learning.get('title', '')
        if not title:
            issues.append("Missing title")
            return ContentQuality(False, 0.0, issues)
        
        # Check if title is promotional section
        if self.is_promo_section_title(title):
            issues.append("Title indicates promotional content")
            return ContentQuality(False, 0.0, issues)
        
        # Clean the title
        clean_title = self.clean_title(title)
        if len(clean_title) < 10:
            issues.append("Title too short after cleaning")
            return ContentQuality(False, 0.0, issues)
        
        # Check content for sponsor material
        content = learning.get('content', learning.get('description', ''))
        if content:
            is_sponsor, reasons = self.is_sponsor_content(content)
            if is_sponsor:
                issues.extend(reasons)
                
                # Try to extract clean content
                clean_content = self.extract_clean_content(content)
                
                # If clean content is too small, reject entirely
                if len(clean_content) < 50:
                    issues.append("No substantial non-promotional content")
                    return ContentQuality(False, 0.0, issues, clean_content)
                else:
                    # Partial success - we have some clean content
                    confidence = min(len(clean_content) / len(content), 0.8)
                    return ContentQuality(True, confidence, issues, clean_content)
        
        # Calculate confidence score
        confidence = 1.0
        
        # Reduce confidence for short content
        if content and len(content) < 100:
            confidence *= 0.7
            issues.append("Content shorter than expected")
        
        # Reduce confidence if no URL
        if not learning.get('url'):
            confidence *= 0.9
            issues.append("No URL provided")
        
        # All good
        if not issues:
            issues.append("High quality content")
        
        return ContentQuality(True, confidence, issues, content)
    
    def parse_learning(self, learning: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse and clean a single learning entry.
        
        Returns cleaned learning dict or None if content is invalid.
        """
        # Assess quality
        quality = self.assess_content_quality(learning)
        
        if not quality.is_valid:
            return None
        
        # Create cleaned version
        cleaned = {
            **learning,
            'title': self.clean_title(learning.get('title', '')),
        }
        
        # Use cleaned content if available
        if quality.cleaned_content:
            if 'content' in learning:
                cleaned['content'] = quality.cleaned_content
            elif 'description' in learning:
                cleaned['description'] = quality.cleaned_content
        
        # Clean description if present
        if 'description' in cleaned:
            cleaned['description'] = self.clean_emoji(cleaned['description'])
        
        # Add quality metadata
        cleaned['quality_score'] = quality.confidence
        cleaned['quality_issues'] = [issue for issue in quality.issues if not issue.startswith("Matches")]
        cleaned['parsed'] = True
        
        return cleaned
    
    def parse_learnings(self, learnings: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parse a list of learnings and return cleaned versions with stats.
        
        Returns:
            Tuple of (cleaned_learnings, stats)
        """
        cleaned = []
        rejected = []
        
        for learning in learnings:
            parsed = self.parse_learning(learning)
            if parsed:
                cleaned.append(parsed)
            else:
                rejected.append({
                    'title': learning.get('title', 'Unknown'),
                    'reason': 'Failed quality assessment'
                })
        
        stats = {
            'total_input': len(learnings),
            'accepted': len(cleaned),
            'rejected': len(rejected),
            'acceptance_rate': len(cleaned) / max(len(learnings), 1),
            'rejected_titles': rejected[:5]  # Sample of rejected
        }
        
        return cleaned, stats


def main():
    """CLI interface for testing the parser"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Intelligent content parser for learnings')
    parser.add_argument('input_file', help='Input JSON file with learnings')
    parser.add_argument('--output', '-o', help='Output file for cleaned learnings')
    parser.add_argument('--stats', action='store_true', help='Print statistics')
    
    args = parser.parse_args()
    
    # Load input
    with open(args.input_file, 'r') as f:
        data = json.load(f)
    
    # Parse learnings
    content_parser = IntelligentContentParser()
    learnings = data.get('learnings', [])
    cleaned, stats = content_parser.parse_learnings(learnings)
    
    # Update data
    data['learnings'] = cleaned
    data['parsing_stats'] = stats
    data['parsed_version'] = '1.0'
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Wrote cleaned learnings to {args.output}")
    else:
        print(json.dumps(data, indent=2))
    
    if args.stats:
        print("\n=== Parsing Statistics ===")
        print(f"Input learnings: {stats['total_input']}")
        print(f"Accepted: {stats['accepted']}")
        print(f"Rejected: {stats['rejected']}")
        print(f"Acceptance rate: {stats['acceptance_rate']:.1%}")
        if stats['rejected_titles']:
            print("\nSample rejected titles:")
            for item in stats['rejected_titles']:
                print(f"  - {item['title']}")


if __name__ == '__main__':
    main()
