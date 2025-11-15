from pydub import AudioSegment, silence

def clip_audio(input_path: str, output_path: str, start_sec: int = 0, clip_duration_sec: int = 15):

    # Step 0: remove silence
    try:
        audio = AudioSegment.from_file(input_path)
    except Exception as e:
        raise ValueError(f"Failed to read audio: {e}")

    # Step 1: Remove silence
    non_silent_chunks = silence.split_on_silence(
        audio,
        min_silence_len=500,  # silence longer than 500ms
        silence_thresh=audio.dBFS - 16,  # silence threshold
        keep_silence=100  # keep 100ms of silence at edges
    )

    if not non_silent_chunks:
        raise ValueError("No non-silent parts detected")

    processed_audio = sum(non_silent_chunks)

    # Step 2: Clip audio
    start_ms = start_sec * 1000
    end_ms = start_ms + clip_duration_sec * 1000

    if len(processed_audio) > end_ms:
        clipped = processed_audio[start_ms:end_ms]
    else:
        clipped = processed_audio

    # Step 3: Resample
    clipped = clipped.set_frame_rate(16000).set_channels(1)
    clipped.export(output_path, format="wav")
    print(f"Saved clipped audio to {output_path}")
