"""
Simplified TTS Generator - F5-TTS with gTTS fallback
"""

from gtts import gTTS
import os
import sys

# Add parent directory to path to import from main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import F5-TTS
try:
    from pipeline.f5tts_synthesizer import synthesize_with_f5tts, F5TTS_AVAILABLE
except ImportError:
    F5TTS_AVAILABLE = False
    print("⚠️ F5-TTS not available. Install with: pip install f5-tts")

# Import Hindi to Romanized converter
try:
    from main import hindi_to_romanized
except ImportError:
    # Fallback function if import fails
    def hindi_to_romanized(text: str) -> str:
    # """Convert Hindi text to Romanized Hindi using proper library"""
        try:
            from indic_transliteration import sanscript
            from indic_transliteration.sanscript import transliterate

            # Convert Hindi (Devanagari) to Romanized
            romanized = transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
            print(f"🔤 Library Romanized: '{text}' -> '{romanized}'")
            return romanized
        except ImportError:
            print("❌ indic-transliteration not installed, using fallback")
            # Fallback simple mapping
            return text.replace('हैलो', 'hello').replace('तुम', 'tum').replace('क्या', 'kya')

def synthesize(text: str, speaker_text: str, speaker_wav: str, output_path: str, lang: str, model: str = "f5tts"):
    """
    Synthesize speech using F5-TTS with gTTS fallback.
    """
    print(f"🎯 TTS INPUT DEBUG: text='{text}', lang='{lang}', speaker_wav='{speaker_wav}'")
    
    # Store original text for gTTS
    original_text = text
    
    # 🚨 ONLY convert Hindi text to Romanized for F5-TTS voice cloning
    if model == "f5tts" and speaker_wav and lang == 'hi' and any('\u0900' <= char <= '\u097F' for char in text):
        romanized_text = hindi_to_romanized(text)
        print(f"🔤 Hindi to Romanized for F5-TTS: '{text}' -> '{romanized_text}'")
        text = romanized_text
        # Also update speaker_text if it's the same
        if speaker_text and any('\u0900' <= char <= '\u097F' for char in speaker_text):
            speaker_text = hindi_to_romanized(speaker_text)
    
    # If no speaker_wav provided, use DEFAULT VOICE (gTTS) - USE ORIGINAL HINDI TEXT
    if not speaker_wav:
        print(f"🔊 Using DEFAULT SYSTEM VOICE (gTTS)")
        print(f"   Text: {original_text}")  # Use original Hindi text
        print(f"   Language: {lang}")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Language mapping for gTTS
            lang_map = {
                'en': 'en', 'hi': 'hi', 'fr': 'fr', 'es': 'es', 
                'de': 'de', 'ja': 'ja', 'ko': 'ko', 'zh': 'zh',
                'ar': 'ar', 'it': 'it', 'pt': 'pt', 'ru': 'ru',
            }
            
            gtts_lang = lang_map.get(lang, 'en')
            print(f"🌐 Using gTTS language: {gtts_lang}")
            
            # Generate TTS with default voice USING ORIGINAL HINDI TEXT
            tts = gTTS(text=original_text, lang=gtts_lang)
            tts.save(output_path)
            
            # Verify file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ DEFAULT VOICE synthesis SUCCESS: {output_path} ({file_size} bytes)")
                return {"model": "gTTS", "success": True, "voice": "default"}
            else:
                print(f"❌ DEFAULT VOICE synthesis FAILED: File not created")
                return {"model": "gTTS", "success": False, "error": "File not created"}
                
        except Exception as e:
            print(f"❌ DEFAULT VOICE ERROR: {e}")
            return {"model": "gTTS", "success": False, "error": str(e)}
    
    # Use F5-TTS if speaker_wav is provided (voice cloning) - USE ROMANIZED TEXT
    elif model == "f5tts" and F5TTS_AVAILABLE and speaker_wav:
        print(f"🎤 Trying F5-TTS VOICE CLONING")
        print(f"   Text: {text}")  # Use Romanized text
        print(f"   Language: {lang}")
        print(f"   Speaker audio: {speaker_wav}")
        
        success = synthesize_with_f5tts(text, speaker_wav, output_path, lang)
        if success:
            print(f"✅ F5-TTS voice cloning successful")
            return {"model": "f5tts", "success": True, "voice": "cloned"}
        else:
            print("❌ F5-TTS failed, falling back to gTTS")
            # Fallback to gTTS - USE ORIGINAL HINDI TEXT
            return synthesize(original_text, "", "", output_path, lang, "gtts")

    # Final fallback
    return {"model": "none", "success": False, "error": "No TTS model available"}