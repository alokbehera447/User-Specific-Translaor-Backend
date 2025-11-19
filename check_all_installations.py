import sys
import os

print("=== COMPREHENSIVE INSTALLATION CHECK ===\n")

checks = []

# 1. Check Python version
print("1. Python Version:")
try:
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    if version.major == 3 and version.minor in [10, 11]:
        checks.append("✓ Python version compatible")
        print("   ✓ Compatible (3.10 or 3.11)")
    else:
        checks.append("⚠ Python version may have issues")
        print("   ⚠ Version might cause compatibility issues")
except Exception as e:
    checks.append("✗ Python version check failed")
    print(f"   ✗ Error: {e}")

# 2. Check virtual environment
print("\n2. Virtual Environment:")
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    checks.append("✓ Running in virtual environment")
    print("   ✓ Virtual environment active")
else:
    checks.append("⚠ Not in virtual environment")
    print("   ⚠ Not in virtual environment")

# 3. Check PyTorch
print("\n3. PyTorch:")
try:
    import torch
    print(f"   ✓ PyTorch {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
    checks.append("✓ PyTorch installed")
except ImportError as e:
    checks.append("✗ PyTorch not installed")
    print(f"   ✗ PyTorch not installed: {e}")

# 4. Check system dependencies via Python packages
print("\n4. Core Dependencies:")
dependencies = [
    ("FastAPI", "fastapi"),
    ("SQLAlchemy", "sqlalchemy"),
    ("SpeechRecognition", "speech_recognition"),
    ("gTTS", "gtts"),
    ("Whisper", "whisper"),
    ("Transformers", "transformers"),
    ("SentencePiece", "sentencepiece"),
    ("Accelerate", "accelerate"),
]

for name, package in dependencies:
    try:
        __import__(package)
        print(f"   ✓ {name}")
        checks.append(f"✓ {name}")
    except ImportError:
        print(f"   ✗ {name}")
        checks.append(f"✗ {name}")

# 5. Check f5-tts
print("\n5. f5-tts:")
try:
    import f5_tts
    print("   ✓ f5-tts installed")
    checks.append("✓ f5-tts")
except ImportError as e:
    print(f"   ✗ f5-tts: {e}")
    checks.append("✗ f5-tts")

# 6. Check Resemble Enhance
print("\n6. Resemble Enhance:")
try:
    import resemble_enhance
    print("   ✓ Resemble Enhance installed")
    checks.append("✓ Resemble Enhance")
except ImportError as e:
    print(f"   ✗ Resemble Enhance: {e}")
    checks.append("✗ Resemble Enhance")

# 7. Check MeCab and unidic
print("\n7. MeCab & Japanese Support:")
try:
    import MeCab
    import unidic
    print("   ✓ MeCab imported")
    
    # Test MeCab functionality
    tagger = MeCab.Tagger()
    result = tagger.parse('こんにちは')
    if result and '名詞' in result or '動詞' in result:
        print("   ✓ MeCab working with Japanese text")
        checks.append("✓ MeCab & unidic")
    else:
        print("   ⚠ MeCab loaded but Japanese parsing unclear")
        checks.append("⚠ MeCab functionality uncertain")
        
except ImportError as e:
    print(f"   ✗ MeCab/unidic: {e}")
    checks.append("✗ MeCab/unidic")

# 8. Check audio/video dependencies
print("\n8. Audio/Video Dependencies:")
audio_deps = [
    ("Librosa", "librosa"),
    ("SoundFile", "soundfile"),
    ("pydub", "pydub"),
]

for name, package in audio_deps:
    try:
        __import__(package)
        print(f"   ✓ {name}")
        checks.append(f"✓ {name}")
    except ImportError:
        print(f"   ✗ {name}")
        checks.append(f"✗ {name}")

# Summary
print("\n" + "="*50)
print("INSTALLATION SUMMARY:")
print("="*50)

successful = sum(1 for check in checks if check.startswith("✓"))
warnings = sum(1 for check in checks if check.startswith("⚠"))
failed = sum(1 for check in checks if check.startswith("✗"))

print(f"Successful: {successful}")
print(f"Warnings: {warnings}") 
print(f"Failed: {failed}")

if failed == 0 and warnings == 0:
    print("\n🎉 ALL INSTALLATIONS COMPLETED SUCCESSFULLY!")
    print("🚀 Your User-Specific Translator Backend is ready!")
elif failed == 0:
    print("\n✅ Core installations successful with some warnings")
    print("📝 Check warnings above")
else:
    print("\n❌ Some installations failed")
    print("🔧 Please check the failed items above")

print("\nDetailed checks:")
for check in checks:
    print(f"  {check}")
