import whisper
import subprocess
import os

model_whisper = whisper.load_model("base")

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
