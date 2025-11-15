import torch

# Check if torch.xpu exists, if not create a dummy attribute
if not hasattr(torch, 'xpu'):
    class DummyXPU:
        def is_available(self):
            return False
    
    torch.xpu = DummyXPU()
    print("✅ Patched torch.xpu for F5-TTS compatibility")

# Now import F5-TTS
try:
    from f5_tts.api import F5TTS
    engine = F5TTS()
    print("✅ F5-TTS loaded successfully after patching!")
except Exception as e:
    print(f"❌ F5-TTS still failed: {e}")
