"""
Text formatter for TTS compatibility
"""
import re
from typing import List, Dict


class TTSFormatter:
    """Formats text for optimal TTS processing"""
    
    # Vietnamese punctuation marks
    SENTENCE_ENDINGS = {'.', '!', '?'}
    
    # Acronyms and technical terms - Vietnamese phonetic spellings with hyphens for TTS
    ACRONYM_REPLACEMENTS = {
        # Technology acronyms
        r'\bAI\b': 'ây-ai',
        r'\bChatGPT\b': 'Chat-gii-pi-ti',
        r'\bGPT\b': 'gii-pi-ti',
        r'\bAPI\b': 'ê-pi-ai',
        r'\bIoT\b': 'ai-ô-ti',
        r'\bVR\b': 'vi-a',
        r'\bAR\b': 'ê-a',
        r'\bML\b': 'em-len',
        r'\b5G\b': 'năm-gờ',
        r'\b4G\b': 'bốn-gờ',
        r'\bWi-Fi\b': 'oai-fai',
        r'\bUSB\b': 'u-ét-bi',
        r'\bSSD\b': 'ét-ét-đi',
        r'\bHDD\b': 'hát-đi-đi',
        r'\bRAM\b': 'ram',
        r'\bCPU\b': 'xi-pi-du',
        r'\bGPU\b': 'gờ-pi-du',
        r'\bVPN\b': 'vi-pi-en',
        r'\bSMS\b': 'ét-em-ét',
        r'\bURL\b': 'u-a-en',
        r'\bPDF\b': 'pi-đi-ép',
        r'\bHTML\b': 'hát-ti-em-en',
        r'\bCSS\b': 'xi-ét-ét',
        
        # Vietnamese tech terms
        r'\bVNeID\b': 'Vi-en-ai-đi',
        r'\bVNPT\b': 'Vi-en-pi-ti',
        r'\bFPT\b': 'ép-pi-ti',
        
        # Organizations (full forms for clarity)
        r'\bTP\.?\s*HCM\b': 'Thành phố Hồ Chí Minh',
        r'\bTP\.?\s*Hồ Chí Minh\b': 'Thành phố Hồ Chí Minh',
        r'\bHĐND\b': 'Hội đồng nhân dân',
        r'\bUBND\b': 'Ủy ban nhân dân',
        r'\bASICO\b': 'a-xích-ô',
        r'\bNCSC\b': 'en-xi-ét-xi',
        
        # Common tech brands (phonetic with hyphens)
        r'\bGoogle\b': 'Gu-gồ',
        r'\bFacebook\b': 'Phây-búc',
        r'\bYouTube\b': 'Diu-túp',
        r'\bTwitter\b': 'Tuy-tơ',
        r'\bLinkedIn\b': 'Linh-đin',
        r'\bInstagram\b': 'In-tờ-ta-gram',
        r'\bTikTok\b': 'Tích-tóc',
        r'\bZalo\b': 'Da-lô',
        r'\bMicrosoft\b': 'Mai-cờ-rô-xốp',
        r'\bApple\b': 'Ép-pồ',
        r'\bSamsung\b': 'Xam-xung',
        r'\bXiaomi\b': 'Sia-o-mi',
        r'\bOppo\b': 'Ốp-pô',
        r'\bVivo\b': 'Vi-vô',
        r'\bHuawei\b': 'Hoa-vây',
        r'\bNokia\b': 'Nô-ki-a',
        r'\bMotorola\b': 'Mô-tô-rô-la',
        r'\bMeta\b': 'Mê-ta',
    }
    
    # Common English phrases that should be translated
    ENGLISH_PHRASES = {
        r'\bMake in Vietnam\b': 'sản xuất tại Việt Nam',
        r'\bMade in Vietnam\b': 'sản xuất tại Việt Nam',
        r'\bsmartphone\b': 'điện thoại thông minh',
        r'\bonline\b': 'trực tuyến',
        r'\boffline\b': 'ngoại tuyến',
        r'\bwebsite\b': 'trang web',
        r'\bemail\b': 'thư điện tử',
        r'\blogin\b': 'đăng nhập',
        r'\blogout\b': 'đăng xuất',
        r'\bupdate\b': 'cập nhật',
        r'\bdownload\b': 'tải xuống',
        r'\bupload\b': 'tải lên',
        r'\bapp\b': 'ứng dụng',
        r'\bapps\b': 'ứng dụng',
        r'\bsoftware\b': 'phần mềm',
        r'\bhardware\b': 'phần cứng',
        r'\bcloud\b': 'đám mây',
        r'\bstreaming\b': 'phát trực tuyến',
        r'\blivestream\b': 'phát trực tiếp',
    }
    
    # Product name patterns - convert numbers to Vietnamese
    PRODUCT_PATTERNS = [
        (r'\biPhone\s+(\d+)', lambda m: f'iPhone {TTSFormatter._number_to_vietnamese(m.group(1))}'),
        (r'\bGalaxy\s+S(\d+)', lambda m: f'Galaxy ét {TTSFormatter._number_to_vietnamese(m.group(1))}'),
        (r'\bGalaxy\s+A(\d+)', lambda m: f'Galaxy a {TTSFormatter._number_to_vietnamese(m.group(1))}'),
        (r'\bGalaxy\s+Z(\d+)', lambda m: f'Galaxy dét {TTSFormatter._number_to_vietnamese(m.group(1))}'),
        (r'\bRedmi\s+(\d+)', lambda m: f'Redmi {TTSFormatter._number_to_vietnamese(m.group(1))}'),
        (r'\bRazr\s+(\d+)', lambda m: f'Razr {TTSFormatter._number_to_vietnamese(m.group(1))}'),
    ]
    
    @staticmethod
    def _number_to_vietnamese(num_str: str) -> str:
        """Convert number to Vietnamese pronunciation"""
        try:
            num = int(num_str)
            if num < 10:
                words = ['không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']
                return words[num]
            elif num < 20:
                words = {10: 'mười', 11: 'mười một', 12: 'mười hai', 13: 'mười ba', 
                        14: 'mười bốn', 15: 'mười lăm', 16: 'mười sáu', 17: 'mười bảy',
                        18: 'mười tám', 19: 'mười chín'}
                return words.get(num, num_str)
            elif num < 100:
                tens = num // 10
                ones = num % 10
                tens_words = ['', '', 'hai mươi', 'ba mươi', 'bốn mươi', 'năm mươi', 
                             'sáu mươi', 'bảy mươi', 'tám mươi', 'chín mươi']
                ones_words = ['', ' một', ' hai', ' ba', ' bốn', ' lăm', ' sáu', ' bảy', ' tám', ' chín']
                if ones == 5 and tens > 1:
                    return tens_words[tens] + ' lăm'
                return tens_words[tens] + ones_words[ones]
            else:
                return num_str
        except:
            return num_str
    
    @staticmethod
    def normalize_acronyms_and_brands(text: str) -> str:
        """
        Replace acronyms and brand names with Vietnamese phonetic spellings
        
        Args:
            text: Input text
        
        Returns:
            Text with normalized acronyms
        """
        # First, translate common English phrases
        for pattern, replacement in TTSFormatter.ENGLISH_PHRASES.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Fix duplicated acronyms BEFORE replacement (e.g., "AI AI" -> "AI")
        # This prevents "AI AI" from becoming "ây-ai ây-ai"
        text = re.sub(r'\b(AI)\s+\1\b', r'\1', text)  # AI AI -> AI
        text = re.sub(r'\b(IoT)\s+\1\b', r'\1', text)  # IoT IoT -> IoT
        text = re.sub(r'\b(VR)\s+\1\b', r'\1', text)  # VR VR -> VR
        
        # Then apply acronym replacements
        # Special handling for AI to avoid matching lowercase "ai" in Vietnamese phonetics
        ai_pattern = r'\bAI\b'
        if ai_pattern in TTSFormatter.ACRONYM_REPLACEMENTS:
            ai_replacement = TTSFormatter.ACRONYM_REPLACEMENTS[ai_pattern]
            text = re.sub(ai_pattern, ai_replacement, text)  # Case-sensitive for AI only
        
        # Apply other replacements with case-insensitive matching
        for pattern, replacement in TTSFormatter.ACRONYM_REPLACEMENTS.items():
            if pattern != ai_pattern:  # Skip AI, already processed
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Finally apply product name patterns
        for pattern, replacement_func in TTSFormatter.PRODUCT_PATTERNS:
            text = re.sub(pattern, replacement_func, text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def capitalize_transitions(text: str) -> str:
        """
        Capitalize transition words at the beginning of sentences
        
        Args:
            text: Input text
        
        Returns:
            Text with properly capitalized transitions
        """
        # Transitions that should be capitalized when starting a sentence
        transitions = [
            'tiếp theo', 'trong khi đó', 'ngoài ra', 
            'tuy nhiên', 'đồng thời', 'bên cạnh đó',
            'mặt khác', 'cuối cùng', 'đặc biệt',
            'chuyển sang', 'về', 'cũng trong'
        ]
        
        for transition in transitions:
            # After sentence ending + space, capitalize transition
            pattern = rf'([.!?]\s+){transition}\b'
            replacement = lambda m: m.group(1) + transition.capitalize()
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def add_punctuation(text: str) -> str:
        """
        Ensure text has proper punctuation
        
        Args:
            text: Input text
        
        Returns:
            Text with proper punctuation
        """
        if not text:
            return ""
        
        text = text.strip()
        
        # Add period at end if missing
        if text and text[-1] not in TTSFormatter.SENTENCE_ENDINGS:
            text += '.'
        
        return text
    
    @staticmethod
    def fix_spacing(text: str) -> str:
        """
        Fix spacing around punctuation
        
        Args:
            text: Input text
        
        Returns:
            Text with corrected spacing
        """
        # Remove space before punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        # Ensure space after punctuation (but not in version numbers)
        text = re.sub(r'([.,!?;:])([^\s\d])', r'\1 \2', text)
        
        # Fix version numbers: "2. 2. 4" -> "2.2.4"
        text = re.sub(r'(\d+)\s*\.\s*(\d+)\s*\.\s*(\d+)', r'\1.\2.\3', text)
        
        # Fix multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def split_long_sentences(text: str, max_length: int = 200) -> str:
        """
        Split overly long sentences for better TTS pacing
        
        Args:
            text: Input text
            max_length: Maximum sentence length in characters
        
        Returns:
            Text with split sentences
        """
        sentences = []
        
        # Split by sentence boundaries
        parts = re.split(r'([.!?])', text)
        
        current_sentence = ""
        
        for i in range(0, len(parts), 2):
            sentence_part = parts[i].strip()
            punctuation = parts[i + 1] if i + 1 < len(parts) else '.'
            
            if not sentence_part:
                continue
            
            full_sentence = sentence_part + punctuation
            
            # If sentence is too long, try to split at commas
            if len(full_sentence) > max_length:
                # Split at commas
                comma_parts = full_sentence.split(',')
                
                for j, comma_part in enumerate(comma_parts):
                    comma_part = comma_part.strip()
                    
                    if j < len(comma_parts) - 1:
                        comma_part += ','
                    
                    if current_sentence and len(current_sentence + ' ' + comma_part) > max_length:
                        sentences.append(current_sentence)
                        current_sentence = comma_part
                    else:
                        if current_sentence:
                            current_sentence += ' ' + comma_part
                        else:
                            current_sentence = comma_part
                
                if current_sentence:
                    sentences.append(current_sentence)
                    current_sentence = ""
            else:
                if current_sentence:
                    sentences.append(current_sentence)
                current_sentence = full_sentence
        
        if current_sentence:
            sentences.append(current_sentence)
        
        return ' '.join(sentences)
    
    @staticmethod
    def normalize_numbers(text: str) -> str:
        """
        Convert numbers to Vietnamese-style format
        
        Args:
            text: Input text
        
        Returns:
            Text with normalized numbers
        """
        # Convert large numbers to Vietnamese style
        # e.g., "1000000" -> "1 triệu"
        
        # This is a simplified version - could be enhanced
        text = re.sub(r'(\d+)\s*triệu', r'\1 triệu', text)
        text = re.sub(r'(\d+)\s*tỷ', r'\1 tỷ', text)
        text = re.sub(r'(\d+)\s*nghìn', r'\1 nghìn', text)
        
        return text
    
    @staticmethod
    def remove_special_chars(text: str) -> str:
        """
        Remove special characters that might cause TTS issues
        
        Args:
            text: Input text
        
        Returns:
            Cleaned text
        """
        # Keep Vietnamese characters, numbers, basic punctuation
        # Remove most special characters
        
        # Keep: letters, numbers, Vietnamese diacritics, basic punctuation, spaces
        text = re.sub(r'[^\w\s.,!?;:()\-""''…àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]', ' ', text)
        
        # Fix multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def add_pauses(text: str) -> str:
        """
        Add natural pauses by ensuring proper punctuation
        
        Args:
            text: Input text
        
        Returns:
            Text with improved pauses
        """
        # Ensure comma after transition words
        transitions = [
            'tiếp theo', 'trong khi đó', 'ngoài ra', 
            'tuy nhiên', 'đồng thời', 'bên cạnh đó'
        ]
        
        for transition in transitions:
            # Add comma after transition if not present
            pattern = rf'\b{transition}\b(?!\s*,)'
            text = re.sub(pattern, rf'{transition},', text, flags=re.IGNORECASE)
        
        return text
    
    def format_for_tts(self, text: str) -> str:
        """
        Complete TTS formatting pipeline
        
        Args:
            text: Input text
        
        Returns:
            TTS-ready text
        """
        # Apply all formatting steps in optimal order
        text = self.remove_special_chars(text)
        text = self.normalize_acronyms_and_brands(text)  # NEW: Normalize before other processing
        text = self.normalize_numbers(text)
        text = self.fix_spacing(text)
        text = self.add_pauses(text)
        text = self.capitalize_transitions(text)  # NEW: Capitalize transitions
        text = self.split_long_sentences(text)
        text = self.add_punctuation(text)
        
        return text
    
    def format_bulletin(
        self,
        bulletin_text: str,
        add_intro: bool = True,
        add_outro: bool = True
    ) -> str:
        """
        Format complete bulletin for TTS
        
        Args:
            bulletin_text: Raw bulletin text
            add_intro: Whether intro is already included
            add_outro: Whether outro is already included
        
        Returns:
            TTS-ready bulletin
        """
        # Format the entire bulletin
        formatted = self.format_for_tts(bulletin_text)
        
        # Ensure proper paragraph breaks
        formatted = re.sub(r'\n\s*\n', '\n\n', formatted)
        
        return formatted
    
    @staticmethod
    def validate_vietnamese_text(text: str) -> bool:
        """
        Validate that text contains Vietnamese characters and is properly formatted
        
        Args:
            text: Text to validate
        
        Returns:
            True if valid Vietnamese text
        """
        if not text or len(text.strip()) < 10:
            return False
        
        # Check for Vietnamese diacritics (indicating Vietnamese text)
        vietnamese_chars = r'[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]'
        
        if not re.search(vietnamese_chars, text.lower()):
            return False
        
        # Check for basic sentence structure (has punctuation)
        if not re.search(r'[.!?]', text):
            return False
        
        return True
