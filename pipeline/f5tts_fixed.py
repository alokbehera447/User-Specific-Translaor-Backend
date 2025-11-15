import torch
import warnings

# Apply the torch.xpu patch before importing F5-TTS
if not hasattr(torch, 'xpu'):
    class DummyXPU:
        def is_available(self):
            return False
        def get_device_name(self, device=None):
            return "CPU"
        def current_device(self):
            return 0
        def device_count(self):
            return 0
    
    torch.xpu = DummyXPU()
    print("✅ Applied torch.xpu compatibility patch for F5-TTS")

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

try:
    from f5_tts.api import F5TTS
    
    class FixedF5TTS:
        def __init__(self):
            self.engine = F5TTS()
            print("✅ F5-TTS engine initialized successfully")
        
        def tts(self, text, speaker_wav, language, output_path):
            """Wrapper for F5-TTS synthesis"""
            return self.engine.tts(
                text=text,
                speaker_wav=speaker_wav,
                language=language,
                output_path=output_path
            )
    
    # Create global instance
    f5_engine = FixedF5TTS()
    F5_TTS_AVAILABLE = True
    
except Exception as e:
    print(f"❌ F5-TTS initialization failed: {e}")
    f5_engine = None
    F5_TTS_AVAILABLE = False
