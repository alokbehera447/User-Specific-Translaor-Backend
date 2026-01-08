# from pipeline.tts_generator import hindi_to_phonetic
import torch

import torchaudio
import os
import re
from pydub import AudioSegment
import numpy as np
import speech_recognition as sr
from pydub.silence import detect_nonsilent

# Import F5-TTS modules
try:
    from f5_tts.api import F5TTS
    F5TTS_AVAILABLE = True
except ImportError:
    F5TTS_AVAILABLE = False
    print("Warning: F5-TTS not installed. Please install with: pip install f5-tts")


def trim_and_transcribe(audio_path, max_duration=11):
    """
    Trims audio to specified duration if longer and converts to text.

    Args:
        audio_path (str): Path to the input audio file
        max_duration (int): Maximum duration in seconds (default: 11)

    Returns:
        tuple: (audio_path, transcription)
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_file(audio_path)

        # Get duration in seconds
        duration_sec = len(audio) / 1000

        # Trim if longer than max_duration
        if duration_sec > max_duration:
            audio = audio[:max_duration * 1000]  # pydub works in milliseconds
            print(f"Audio trimmed from {duration_sec:.2f}s to {max_duration}s")

        # Create output path for trimmed audio
        base_name = os.path.splitext(audio_path)[0]
        output_path = f"{base_name}_trimmed.wav"

        # Export as WAV for speech recognition
        audio.export(output_path, format="wav")

        # Convert audio to text using speech recognition
        recognizer = sr.Recognizer()

        with sr.AudioFile(output_path) as source:
            audio_data = recognizer.record(source)

            # Try to recognize speech
            try:
                text = recognizer.recognize_google(audio_data)
                print(f"Transcription successful: {text[:50]}...")
            except sr.UnknownValueError:
                text = "Could not understand audio"
            except sr.RequestError as e:
                text = f"Could not request results; {e}"

        return output_path, text

    except Exception as e:
        print(f"Error in trim_and_transcribe: {str(e)}")
        return audio_path, "Transcription failed"


def split_into_sentences(text):
    """Split text into sentences using regex"""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s]


class F5TTSSynthesizer:
    """Wrapper class for F5-TTS model"""

    def __init__(self, model_type="F5-TTS", device=None):
        if not F5TTS_AVAILABLE:
            raise ImportError("F5-TTS is not installed. Install with: pip install f5-tts")

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = device
        print(f"Loading F5-TTS model on {device}...")

        # Map model_type to model name
        model_map = {
            "F5-TTS": "F5TTS_Base",
            "E2-TTS": "E2TTS_Base"
        }
        model_name = model_map.get(model_type, "E2TTS_Base")

        # Initialize F5-TTS
        self.f5tts = F5TTS(
            model=model_name,
            device=device
        )

        print("F5-TTS model loaded successfully!")

    def generate_audio(self, text, reference_audio_path, reference_text, output_path):
        """
        Generate audio using F5-TTS

        Args:
            text: Text to generate speech for
            reference_audio_path: Path to reference audio
            reference_text: Transcription of reference audio
            output_path: Path to save generated audio
        """
        print(f"Generating audio with F5-TTS for: {text[:50]}...")

        # Generate audio
        generated_audio, sr, _ = self.f5tts.infer(
            ref_file=reference_audio_path,
            ref_text=reference_text,
            gen_text=text,
            remove_silence=True,
            # speed=0.7,
            # pitch=1.0,
            # energy=1.0,
            # temperature=0.7
        )

        # Convert numpy array to torch tensor if needed
        if isinstance(generated_audio, np.ndarray):
            generated_audio = torch.from_numpy(generated_audio)

        # Ensure correct shape for torchaudio.save: [channels, samples]
        if generated_audio.dim() == 1:
            generated_audio = generated_audio.unsqueeze(0)  # Add channel dimension

        # Save audio
        torchaudio.save(output_path, generated_audio.cpu(), sr)
        print(f"Audio saved to: {output_path}")
        return output_path


def synthesize_with_f5tts(text: str, speaker_wav: str, output_path: str, lang: str = "en"):
    """
    Synthesize speech using F5-TTS

    Args:
        text: Text to synthesize
        speaker_wav: Path to reference speaker audio
        output_path: Path to save output audio
        lang: Language code (not used in F5-TTS but kept for API compatibility)

    Returns:
        bool: True if synthesis successful
    """
    from pipeline.tts_generator import hindi_to_simple_roman

    try:
        if not F5TTS_AVAILABLE:
            raise ImportError("F5-TTS not available")

        print(f"Step 3: Starting F5-TTS synthesis...")
        print(f"Text: {text}")
        print(f"Reference audio: {speaker_wav}")

        # Initialize F5-TTS model (singleton pattern would be better for production)
        f5tts_model = F5TTSSynthesizer()

        # Get reference audio transcription
        print("Transcribing reference audio...")
        ref_audio_path, ref_text = trim_and_transcribe(speaker_wav, max_duration=11)

        if ref_text not in ["Could not understand audio", "Transcription failed"]:
            if lang == "hi" and any('\u0900' <= c <= '\u097F' for c in ref_text):
                ref_text = hindi_to_simple_roman(ref_text)
        else:
            ref_text = "sample reference audio"


        print(f"Reference transcription: {ref_text[:100]}...")

        # Split text into sentences for better quality
        # sentences = split_into_sentences(text)
        if lang == "hi":
            sentences = [text]
        else:
            sentences = split_into_sentences(text)

        print(sentences," ", ref_audio_path, " ", ref_text, " ",output_path)

        if len(sentences) > 1:
            # Generate audio for each sentence and combine
            temp_files = []
            temp_dir = os.path.dirname(output_path)

            for i, sentence in enumerate(sentences):
                temp_output = os.path.join(temp_dir, f"temp_sentence_{i}.wav")
                f5tts_model.generate_audio(sentence, ref_audio_path, ref_text, temp_output)
                temp_files.append(temp_output)

            # Combine audio files
            combined = AudioSegment.empty()
            pause = AudioSegment.silent(duration=150)  # 300ms pause between sentences

            for audio_file in temp_files:
                audio_segment = AudioSegment.from_wav(audio_file)
                combined += audio_segment + pause

            # Remove last pause
            if len(temp_files) > 0:
                combined = combined[:-300]

            # Export combined audio
            combined.export(output_path, format="wav")

            # Clean up temp files
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass
        else:
            # Single sentence, generate directly
            f5tts_model.generate_audio(text, ref_audio_path, ref_text, output_path)

        print(f"Step 3: F5-TTS synthesis completed successfully!")
        return True

    except Exception as e:
        print(f"Error in F5-TTS synthesis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False