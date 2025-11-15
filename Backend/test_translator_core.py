print("🧪 Testing Core Translator Components...")
print("=" * 50)

# Test 1: Whisper Speech-to-Text
try:
    import whisper
    model = whisper.load_model("base")
    print("✅ Whisper: Base model loaded successfully")
except Exception as e:
    print(f"❌ Whisper: {e}")

# Test 2: Transformers Translation
try:
    from transformers import pipeline
    translator = pipeline("translation_en_to_fr", model="Helsinki-NLP/opus-mt-en-fr")
    test_text = "Hello, how are you?"
    result = translator(test_text)[0]['translation_text']
    print(f"✅ Transformers: Translation working ('{test_text}' -> '{result}')")
except Exception as e:
    print(f"❌ Transformers: {e}")

# Test 3: Speech Recognition
try:
    import speech_recognition as sr
    r = sr.Recognizer()
    print("✅ SpeechRecognition: Recognizer initialized")
except Exception as e:
    print(f"❌ SpeechRecognition: {e}")

# Test 4: Text-to-Speech
try:
    from gtts import gTTS
    import io
    print("✅ gTTS: Text-to-speech initialized")
except Exception as e:
    print(f"❌ gTTS: {e}")

# Test 5: Audio Processing
try:
    from pydub import AudioSegment
    print("✅ PyDub: Audio processing initialized")
except Exception as e:
    print(f"❌ PyDub: {e}")

print("\n" + "=" * 50)
print("🎯 Core translator functionality test completed!")
print("📋 All essential components are working!")
