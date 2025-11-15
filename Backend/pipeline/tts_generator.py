"""
Simplified TTS Generator - F5-TTS with gTTS fallback

This module provides text-to-speech synthesis using:
- F5-TTS: Advanced zero-shot voice cloning
- gTTS: Fallback for basic TTS without voice cloning
"""

from gtts import gTTS

# Try to import F5-TTS
try:
    from pipeline.f5tts_synthesizer import synthesize_with_f5tts, F5TTS_AVAILABLE
except ImportError:
    F5TTS_AVAILABLE = False
    print("⚠️ F5-TTS not available. Install with: pip install f5-tts")


def synthesize(text: str, speaker_text: str, speaker_wav: str, output_path: str, lang: str, model: str = "f5tts"):
    """
    Synthesize speech using F5-TTS with gTTS fallback.

    Args:
        text: Text to synthesize (translated text)
        speaker_text: Original transcription text (for F5-TTS reference)
        speaker_wav: Path to reference speaker audio for voice cloning
        output_path: Path to save output audio
        lang: Language code (ISO 639-1 format, e.g., 'en', 'fr', 'es')
        model: TTS model to use ("f5tts" or "gtts")

    Returns:
        dict: Status information including model used and success
    """

    # Use F5-TTS if available and requested
    if model == "f5tts" and F5TTS_AVAILABLE:
        print(f"🎤 Using F5-TTS for voice cloning")
        print(f"   Text: {text[:100]}...")
        print(f"   Language: {lang}")
        success = synthesize_with_f5tts(text, speaker_wav, output_path, lang)
        if success:
            return {"model": "f5tts", "success": True}
        else:
            print("⚠️ F5-TTS failed, falling back to gTTS")
            model = "gtts"

    # Use gTTS as fallback or if explicitly requested
    if model == "gtts" or not F5TTS_AVAILABLE:
        print(f"🔊 Using gTTS for basic TTS")
        print(f"   Text: {text[:100]}...")
        print(f"   Language: {lang}")
        try:
            tts = gTTS(text=text, lang=lang)
            tts.save(output_path)
            print(f"✅ gTTS synthesis complete. Output: {output_path}")
            return {"model": "gtts", "success": True}
        except Exception as e:
            print(f"❌ gTTS failed: {e}")
            return {"model": "gtts", "success": False, "error": str(e)}

    # If we get here, something went wrong
    return {"model": "none", "success": False, "error": "No TTS model available"}
