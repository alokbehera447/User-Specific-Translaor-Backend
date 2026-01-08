import subprocess
import os
import speech_recognition as sr
# import torch
from faster_whisper import WhisperModel

# Load model ONCE (GPU)
# _model = WhisperModel(
#     "base",
#     device="cuda",
#     compute_type="float16"  # best for RTX 4090
# )

_model = WhisperModel(
    "medium",
    device="cpu",
    compute_type="int8"
)
# device = "cuda" if torch.cuda.is_available() else "cpu"
# compute_type = "float16" if device == "cuda" else "int8"

# _model = WhisperModel(
#     "medium",
#     device=device,
#     compute_type=compute_type
# )

def transcribe_hindi(audio_path: str) -> str:
    """Transcribe Hindi audio using Google Speech Recognition"""
    recognizer = sr.Recognizer()
    
    try:
        print("🎯 Using Google Speech Recognition for Hindi...")
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='hi-IN')
            print(f"✅ Google Hindi Transcription: {text}")
            return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""
    except Exception:
        return ""


def transcribe(audio_path: str, language: str = "en") -> str:
    """
    Transcribe audio using Faster-Whisper (GPU).
    Keeps your ffmpeg preprocessing unchanged.
    """

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    safe_wav_path = os.path.splitext(audio_path)[0] + "_converted.wav"

    # Convert to 16kHz mono WAV
    subprocess.run([
        "ffmpeg", "-y",
        "-i", audio_path,
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        safe_wav_path
    ], check=True)

    # Faster-Whisper transcription
    segments, info = _model.transcribe(
        safe_wav_path,
        language=language
    )

    text = " ".join(segment.text for segment in segments)

    try:
        os.remove(safe_wav_path)
    except Exception:
        pass

    print("✅ Transcription completed:", language, text)
    return text
