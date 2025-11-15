import numpy as np
import soundfile as sf
import librosa
import noisereduce as nr
from scipy import signal
import os


def enhance_audio(input_path: str, output_path: str, target_sr: int = 16000) -> str:
    """
    Enhance audio quality for better voice cloning results.

    Steps:
    1. Load and resample audio to consistent sample rate
    2. Remove noise using spectral gating
    3. Normalize audio levels
    4. Apply bandpass filter to focus on speech frequencies (80Hz-8kHz)
    5. Apply pre-emphasis to boost high frequencies

    Args:
        input_path: Path to input audio file
        output_path: Path to save enhanced audio
        target_sr: Target sample rate (default 16000 Hz)

    Returns:
        Path to enhanced audio file
    """
    print(f"🎵 Enhancing audio: {input_path}")

    try:
        # Load audio
        audio, sr = librosa.load(input_path, sr=None)
        print(f"  Original sample rate: {sr} Hz, duration: {len(audio)/sr:.2f}s")

        # Resample if needed
        if sr != target_sr:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
            sr = target_sr
            print(f"  Resampled to: {target_sr} Hz")

        # 1. Noise reduction using spectral gating
        reduced_noise = nr.reduce_noise(
            y=audio,
            sr=sr,
            stationary=False,  # Non-stationary noise reduction
            prop_decrease=0.8   # Reduce noise by 80%
        )
        print("  ✓ Noise reduction applied")

        # 2. Normalize audio to prevent clipping
        # Use peak normalization to -1 dB to leave headroom
        peak = np.abs(reduced_noise).max()
        if peak > 0:
            reduced_noise = reduced_noise / peak * 0.95
        print("  ✓ Audio normalized")

        # 3. Bandpass filter for speech frequencies (80 Hz - 8000 Hz)
        # Most human speech energy is between 80-8000 Hz
        nyquist = sr / 2
        low_freq = 80 / nyquist
        high_freq = min(8000 / nyquist, 0.99)  # Ensure below Nyquist

        sos = signal.butter(4, [low_freq, high_freq], btype='band', output='sos')
        filtered_audio = signal.sosfilt(sos, reduced_noise)
        print("  ✓ Bandpass filter applied (80-8000 Hz)")

        # 4. Pre-emphasis filter to boost high frequencies
        # This helps with clarity and intelligibility
        pre_emphasis = 0.97
        emphasized_audio = np.append(
            filtered_audio[0],
            filtered_audio[1:] - pre_emphasis * filtered_audio[:-1]
        )
        print("  ✓ Pre-emphasis applied")

        # 5. Final normalization
        peak = np.abs(emphasized_audio).max()
        if peak > 0:
            emphasized_audio = emphasized_audio / peak * 0.95

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save enhanced audio
        sf.write(output_path, emphasized_audio, sr)
        print(f"✅ Enhanced audio saved to: {output_path}")

        return output_path

    except Exception as e:
        print(f"❌ Audio enhancement failed: {e}")
        print(f"   Using original audio: {input_path}")
        # If enhancement fails, return original path
        return input_path


def enhance_audio_simple(input_path: str, output_path: str, target_sr: int = 16000) -> str:
    """
    Simplified audio enhancement (fallback if noisereduce not available).

    Args:
        input_path: Path to input audio file
        output_path: Path to save enhanced audio
        target_sr: Target sample rate (default 16000 Hz)

    Returns:
        Path to enhanced audio file
    """
    print(f"🎵 Enhancing audio (simple mode): {input_path}")

    try:
        # Load audio
        audio, sr = librosa.load(input_path, sr=target_sr)

        # Normalize
        peak = np.abs(audio).max()
        if peak > 0:
            audio = audio / peak * 0.95

        # Bandpass filter
        nyquist = sr / 2
        low_freq = 80 / nyquist
        high_freq = min(8000 / nyquist, 0.99)
        sos = signal.butter(4, [low_freq, high_freq], btype='band', output='sos')
        audio = signal.sosfilt(sos, audio)

        # Final normalization
        peak = np.abs(audio).max()
        if peak > 0:
            audio = audio / peak * 0.95

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save
        sf.write(output_path, audio, sr)
        print(f"✅ Enhanced audio saved to: {output_path}")

        return output_path

    except Exception as e:
        print(f"❌ Audio enhancement failed: {e}")
        return input_path
