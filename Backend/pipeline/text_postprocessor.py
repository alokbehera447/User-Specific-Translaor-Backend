# pipeline/text_postprocessor.py

def clean_transcription(text):
    """
    Clean and normalize transcription text
    """
    if not text:
        return ""
    
    # Basic cleaning
    text = text.strip()
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Ensure proper capitalization for sentences
    if text and text[-1] not in ['.', '!', '?']:
        text += '.'
    
    return text

def clean_translation(text):
    """
    Clean and normalize translation text
    """
    if not text:
        return ""
    
    # Basic cleaning
    text = text.strip()
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Ensure proper punctuation
    if text and text[-1] not in ['.', '!', '?']:
        text += '.'
    
    return text

def normalize_text(text):
    """
    Normalize text for TTS processing
    """
    if not text:
        return ""
    
    text = text.strip()
    text = ' '.join(text.split())
    
    # Remove special characters that might cause TTS issues
    import re
    text = re.sub(r'[^\w\s.,!?\-]', '', text)
    
    return text
