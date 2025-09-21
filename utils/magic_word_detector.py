import re
from typing import List, Tuple, Optional

class MagicWordDetector:
    """Detects magic words in user prompts that trigger code execution."""
    
    def __init__(self, magic_words: Optional[List[str]] = None):
        """Initialize with default or custom magic words."""
        if magic_words is None:
            self.magic_words = [
                "EXECUTE",
                "RUN_CODE", 
                "CODE_EXEC",
                "SHELL_EXEC",
                "PYTHON_EXEC",
                "ANALYZE_DATA",
                "PROCESS_DATA",
                "COMPUTE",
                "CALCULATE"
            ]
        else:
            self.magic_words = magic_words
        
        # Create regex patterns for each magic word (case insensitive)
        self.patterns = [
            re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE) 
            for word in self.magic_words
        ]
    
    def detect_magic_words(self, text: str) -> Tuple[bool, List[str], str]:
        """
        Detect magic words in text.
        
        Returns:
            - bool: True if any magic word is found
            - List[str]: List of detected magic words
            - str: Cleaned text with magic words removed (optional)
        """
        detected_words = []
        cleaned_text = text
        
        for i, pattern in enumerate(self.patterns):
            matches = pattern.findall(text)
            if matches:
                detected_words.extend([self.magic_words[i]] * len(matches))
                # Remove magic words from text for cleaner processing
                cleaned_text = pattern.sub('', cleaned_text)
        
        # Clean up extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        has_magic_words = len(detected_words) > 0
        return has_magic_words, detected_words, cleaned_text
    
    def should_trigger_execution(self, text: str) -> bool:
        """Simple check if text should trigger code execution."""
        has_magic, _, _ = self.detect_magic_words(text)
        return has_magic
    
    def extract_execution_intent(self, text: str) -> dict:
        """
        Extract execution intent and context from text.
        
        Returns a dictionary with:
        - has_magic_word: bool
        - detected_words: List[str] 
        - cleaned_text: str
        - execution_type: str (inferred type of execution needed)
        """
        has_magic, detected_words, cleaned_text = self.detect_magic_words(text)
        
        # Infer execution type based on context
        execution_type = "general"
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["python", "script", "code"]):
            execution_type = "python"
        elif any(word in text_lower for word in ["shell", "bash", "command"]):
            execution_type = "shell"
        elif any(word in text_lower for word in ["analyze", "analysis", "data"]):
            execution_type = "data_analysis"
        elif any(word in text_lower for word in ["calculate", "compute", "math"]):
            execution_type = "calculation"
        elif any(word in text_lower for word in ["process", "transform", "convert"]):
            execution_type = "data_processing"
        
        return {
            "has_magic_word": has_magic,
            "detected_words": detected_words,
            "cleaned_text": cleaned_text,
            "execution_type": execution_type,
            "original_text": text
        }

# Global instance for easy access
default_detector = MagicWordDetector()

def detect_magic_words(text: str) -> Tuple[bool, List[str], str]:
    """Convenience function using default detector."""
    return default_detector.detect_magic_words(text)

def should_trigger_execution(text: str) -> bool:
    """Convenience function to check if execution should be triggered."""
    return default_detector.should_trigger_execution(text)

def extract_execution_intent(text: str) -> dict:
    """Convenience function to extract execution intent."""
    return default_detector.extract_execution_intent(text)

if __name__ == "__main__":
    # Test the magic word detector
    detector = MagicWordDetector()
    
    test_cases = [
        "Please EXECUTE some code to analyze this data",
        "Can you RUN_CODE to calculate the average?",
        "I need help with Python programming",
        "ANALYZE_DATA from the website and show me trends",
        "Just answer my question normally",
        "COMPUTE the total sales from the data",
        "Execute this: print('hello world')",
        "Can you process data and CALCULATE statistics?"
    ]
    
    print("Testing Magic Word Detection:")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{test_text}'")
        
        intent = detector.extract_execution_intent(test_text)
        print(f"  Has magic word: {intent['has_magic_word']}")
        print(f"  Detected words: {intent['detected_words']}")
        print(f"  Execution type: {intent['execution_type']}")
        print(f"  Cleaned text: '{intent['cleaned_text']}'")
