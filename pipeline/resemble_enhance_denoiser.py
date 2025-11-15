"""
Resemble Enhance Audio Denoiser Module

This module provides audio denoising functionality using Resemble Enhance,
which uses AI to separate speech from noisy audio and improve overall quality.
"""

import os
import torch
import torchaudio
from resemble_enhance.enhancer.inference import denoise


def denoise_audio(input_path: str, output_path: str, device: str = "cpu") -> str:
    """
    Denoise audio using Resemble Enhance AI model.

    This function:
    1. Loads the input audio file
    2. Converts to mono if stereo
    3. Resamples to 44.1kHz (required by Resemble Enhance)
    4. Applies AI-based denoising
    5. Saves the denoised audio

    Args:
        input_path: Path to input audio file (any format supported by torchaudio)
        output_path: Path to save denoised audio (will be saved as WAV)
        device: Device to run inference on ("cpu" or "cuda")

    Returns:
        Path to denoised audio file

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If audio processing fails
    """
    print(f"🎵 Denoising audio with Resemble Enhance: {input_path}")

    try:
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Load audio
        wav, sr = torchaudio.load(input_path)
        print(f"  Original sample rate: {sr} Hz, channels: {wav.shape[0]}, duration: {wav.shape[1]/sr:.2f}s")

        # Convert to mono if stereo (average channels)
        if wav.shape[0] > 1:
            wav = torch.mean(wav, dim=0)  # Average channels to mono
            print("  ✓ Converted stereo to mono")
        else:
            wav = wav.squeeze(0)  # Remove channel dimension if already mono [1, N] -> [N]

        # Validate waveform shape
        if wav.dim() != 1:
            raise ValueError(f"Expected 1D waveform after processing, got {wav.dim()}D with shape {wav.shape}")

        # Resample to 44.1kHz (required by Resemble Enhance)
        if sr != 44100:
            resampler = torchaudio.transforms.Resample(sr, 44100)
            wav = resampler(wav)
            sr = 44100
            print(f"  ✓ Resampled to 44.1kHz")

        # Move to specified device (cpu or cuda)
        wav = wav.to(device)
        print(f"  ✓ Using device: {device}")

        # Apply Resemble Enhance denoising
        print("  🔄 Applying AI denoising (this may take a moment)...")
        denoised_wav, denoised_sr = denoise(wav, sr, device=device)
        print("  ✓ Denoising complete")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

        # Move back to CPU for saving
        denoised_wav = denoised_wav.cpu()

        # Ensure correct shape for saving (add channel dimension if needed)
        if denoised_wav.dim() == 1:
            denoised_wav = denoised_wav.unsqueeze(0)  # [N] -> [1, N]

        # Save denoised audio
        torchaudio.save(output_path, denoised_wav, denoised_sr)
        print(f"✅ Denoised audio saved to: {output_path}")

        return output_path

    except Exception as e:
        print(f"❌ Audio denoising failed: {e}")
        print(f"   Using original audio: {input_path}")
        # If denoising fails, return original path as fallback
        return input_path


def denoise_audio_simple(input_path: str, output_path: str) -> str:
    """
    Simplified denoising with basic error handling.

    This is a convenience wrapper around denoise_audio() that uses
    default CPU settings and provides simpler error handling.

    Args:
        input_path: Path to input audio file
        output_path: Path to save denoised audio

    Returns:
        Path to denoised audio file (or original if denoising fails)
    """
    try:
        return denoise_audio(input_path, output_path, device="cpu")
    except Exception as e:
        print(f"⚠️ Denoising failed, using original audio: {e}")
        return input_path
