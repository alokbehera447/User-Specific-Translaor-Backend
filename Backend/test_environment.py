import sys
print(f"Python version: {sys.version}\n")

# Test critical packages
packages = [
    ("torch", "PyTorch"),
    ("torchvision", "TorchVision"),
    ("torchaudio", "TorchAudio"), 
    ("whisper", "Whisper"),
    ("transformers", "Transformers"),
    ("speech_recognition", "SpeechRecognition"),
    ("fastapi", "FastAPI"),
]

print("Package Status:")
print("-" * 30)

for package, name in packages:
    try:
        __import__(package)
        version = getattr(__import__(package), '__version__', 'OK')
        print(f"✓ {name}: {version}")
    except ImportError as e:
        print(f"✗ {name}: {e}")

# Test PyTorch
try:
    import torch
    print(f"\nPyTorch Device: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
except:
    pass

print("\nEnvironment test completed!")
