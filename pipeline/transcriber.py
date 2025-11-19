import whisper
import subprocess
import os
import speech_recognition as sr

model_whisper = whisper.load_model("base")

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
        print("❌ Google could not understand Hindi audio")
        return ""
    except sr.RequestError as e:
        print(f"❌ Google Speech Recognition error: {e}")
        return ""
    except Exception as e:
        print(f"❌ Google Speech Recognition failed: {e}")
        return ""

def transcribe(audio_path: str, language: str = "en") -> str:
    """
    Safely transcribe any audio format (m4a, mp3, wav, etc.) to text using Whisper.
    Automatically converts input to 16kHz mono WAV before transcription.
    """

    # ✅ Step 1: Ensure input file exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # ✅ Step 2: Convert input audio to a standard WAV (16kHz mono)
    safe_wav_path = os.path.splitext(audio_path)[0] + "_converted.wav"

    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-i", audio_path,
            "-ar", "16000",  # sample rate
            "-ac", "1",       # mono
            "-c:a", "pcm_s16le",
            safe_wav_path
        ], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print("❌ FFmpeg conversion failed:", e.stderr.decode())
        raise RuntimeError(f"Failed to convert audio: {audio_path}")

    # ✅ Step 3: Transcribe with Whisper
    result = model_whisper.transcribe(safe_wav_path, language=language)
    print("✅ Transcription completed:", language, result['text'])

    # ✅ Step 4: Clean up temp file
    try:
        os.remove(safe_wav_path)
    except Exception:
        pass

    return result["text"]