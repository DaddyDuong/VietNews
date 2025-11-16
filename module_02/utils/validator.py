"""
Output validator for bulletin quality checks
"""
import re
from typing import Dict, List, Tuple


class BulletinValidator:
    """Validates bulletin output quality"""
    
    @staticmethod
    def validate_bulletin_structure(bulletin: Dict) -> Tuple[bool, List[str]]:
        """
        Validate bulletin structure
        
        Args:
            bulletin: Bulletin dictionary
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        required_fields = [
            'bulletin_date',
            'summary',
            'total_articles_processed',
            'stories',
            'full_bulletin'
        ]
        
        for field in required_fields:
            if field not in bulletin:
                errors.append(f"Missing required field: {field}")
        
        # Validate stories
        if 'stories' in bulletin:
            if not isinstance(bulletin['stories'], list):
                errors.append("'stories' must be a list")
            elif len(bulletin['stories']) == 0:
                errors.append("'stories' list is empty")
            else:
                # Validate each story
                for i, story in enumerate(bulletin['stories']):
                    story_errors = BulletinValidator._validate_story(story, i)
                    errors.extend(story_errors)
        
        # Validate full_bulletin
        if 'full_bulletin' in bulletin:
            text = bulletin['full_bulletin']
            if not text or len(text.strip()) < 100:
                errors.append("'full_bulletin' is too short or empty")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_story(story: Dict, index: int) -> List[str]:
        """Validate individual story structure"""
        errors = []
        prefix = f"Story {index + 1}"
        
        required_fields = ['topic', 'priority', 'content', 'sources']
        
        for field in required_fields:
            if field not in story:
                errors.append(f"{prefix}: Missing required field '{field}'")
        
        # Validate priority
        if 'priority' in story:
            priority = story['priority']
            if not isinstance(priority, int) or not (1 <= priority <= 10):
                errors.append(f"{prefix}: 'priority' must be integer between 1-10")
        
        # Validate content
        if 'content' in story:
            content = story['content']
            if not content or len(content.strip()) < 20:
                errors.append(f"{prefix}: 'content' is too short")
        
        # Validate sources
        if 'sources' in story:
            if not isinstance(story['sources'], list) or len(story['sources']) == 0:
                errors.append(f"{prefix}: 'sources' must be non-empty list")
        
        return errors
    
    @staticmethod
    def validate_vietnamese_text(text: str) -> Tuple[bool, List[str]]:
        """
        Validate Vietnamese text quality
        
        Args:
            text: Text to validate
        
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Check minimum length
        if len(text.strip()) < 50:
            warnings.append("Text is too short")
            return False, warnings
        
        # Check for Vietnamese diacritics
        vietnamese_chars = r'[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]'
        if not re.search(vietnamese_chars, text.lower()):
            warnings.append("Text may not be Vietnamese (no diacritics found)")
        
        # Check for proper punctuation
        if not re.search(r'[.!?]', text):
            warnings.append("Text lacks proper sentence punctuation")
        
        # Check for overly long sentences
        sentences = re.split(r'[.!?]+', text)
        for i, sentence in enumerate(sentences):
            if len(sentence) > 300:
                warnings.append(f"Sentence {i + 1} is very long ({len(sentence)} chars)")
        
        # Check for English text (might indicate poor translation)
        english_words = re.findall(r'\b[A-Z][a-z]+\b', text)
        # Exclude common tech names
        common_tech_names = {
            'iPhone', 'iPad', 'Google', 'Microsoft', 'Apple', 'Samsung',
            'Facebook', 'Meta', 'Twitter', 'ChatGPT', 'AI', 'TikTok'
        }
        english_words = [w for w in english_words if w not in common_tech_names]
        
        if len(english_words) > 5:
            warnings.append(f"Contains many English words: {', '.join(english_words[:5])}")
        
        return len(warnings) == 0, warnings
    
    @staticmethod
    def validate_tts_compatibility(text: str) -> Tuple[bool, List[str]]:
        """
        Validate TTS compatibility
        
        Args:
            text: Text to validate
        
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Check for URLs (shouldn't be in TTS text)
        if re.search(r'http[s]?://', text):
            warnings.append("Text contains URLs (not suitable for TTS)")
        
        # Check for email addresses
        if re.search(r'\S+@\S+', text):
            warnings.append("Text contains email addresses")
        
        # Check for code snippets or special formatting
        if re.search(r'[{}[\]<>]', text):
            warnings.append("Text contains special characters that may affect TTS")
        
        # Check for numbers without context
        isolated_numbers = re.findall(r'\b\d{4,}\b', text)
        if len(isolated_numbers) > 3:
            warnings.append("Text contains many isolated numbers (may sound unnatural)")
        
        # Check for excessive capitalization
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            warnings.append("Text has excessive capitalization")
        
        return len(warnings) == 0, warnings
    
    @staticmethod
    def validate_complete(bulletin: Dict, full_text: str) -> Dict:
        """
        Run complete validation suite
        
        Args:
            bulletin: Bulletin dictionary
            full_text: Full bulletin text
        
        Returns:
            Validation report dictionary
        """
        report = {
            "structure_valid": False,
            "vietnamese_valid": False,
            "tts_compatible": False,
            "errors": [],
            "warnings": []
        }
        
        # Structure validation
        struct_valid, struct_errors = BulletinValidator.validate_bulletin_structure(bulletin)
        report["structure_valid"] = struct_valid
        report["errors"].extend(struct_errors)
        
        # Vietnamese text validation
        viet_valid, viet_warnings = BulletinValidator.validate_vietnamese_text(full_text)
        report["vietnamese_valid"] = viet_valid
        report["warnings"].extend([f"Vietnamese: {w}" for w in viet_warnings])
        
        # TTS compatibility validation
        tts_valid, tts_warnings = BulletinValidator.validate_tts_compatibility(full_text)
        report["tts_compatible"] = tts_valid
        report["warnings"].extend([f"TTS: {w}" for w in tts_warnings])
        
        # Overall validation
        report["is_valid"] = struct_valid and viet_valid and tts_valid
        
        return report
