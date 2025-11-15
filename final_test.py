import sys
print("🎯 Final Environment Test")
print("=" * 40)
print(f"Python: {sys.version}\n")

packages = [
    ("torch", "PyTorch"),
    ("torchvision", "TorchVision"),
    ("torchaudio", "TorchAudio"),
    ("whisper", "Whisper"),
    ("transformers", "Transformers"),
    ("speech_recognition", "SpeechRecognition"),
    ("fastapi", "FastAPI"),
    ("pydub", "PyDub"),
    ("gtts", "gTTS"),
]

print("Package Status:")
print("-" * 30)

all_ok = True
for package, name in packages:
    try:
        __import__(package)
        version = getattr(__import__(package), '__version__', 'OK')
        print(f"✅ {name}: {version}")
    except ImportError as e:
        print(f"❌ {name}: {e}")
        all_ok = False

# Test PyTorch
try:
    import torch
    print(f"\n🔧 PyTorch Details:")
    print(f"   Version: {torch.__version__}")
    print(f"   CUDA: {torch.cuda.is_available()}")
    print(f"   Device: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
except Exception as e:
    print(f"PyTorch test failed: {e}")

print("\n" + "=" * 40)
if all_ok:
    print("🎉 ALL PACKAGES INSTALLED SUCCESSFULLY!")
    print("🚀 Your translator backend is ready to run!")
else:
    print("⚠️  Some packages missing, but core functionality should work.")

print("\nNext step: Start your backend server with:")
print("uvicorn main:app --reload --port 8000 --host 127.0.0.1")
