#uvicorn main:app --reload --port 8000 --host 127.0.0.1
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
import os, shutil
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from typing import Optional
from pipeline.transcriber import transcribe
from pipeline.translator import translate
from pipeline.tts_generator import synthesize
from pipeline.utils import clip_audio
from pipeline.lang_code import nllb_to_whisper_lang_code
from pipeline.resemble_enhance_denoiser import denoise_audio
from pipeline.text_postprocessor import clean_transcription, clean_translation
import speech_recognition as sr
import torch
import torchaudio

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from login.auth import authenticate_user, create_access_token, get_user, pwd_context,  validate_and_get_user
from login.models import User, SavedAccent
from login.database import get_db
import tempfile
import asyncio
from starlette.requests import Request
import re
import subprocess

app = FastAPI()


# Helper function to convert email to username
def email_to_username(email: str) -> str:
    """Convert email to a safe username for file storage"""
    # Extract the part before @ and sanitize it
    username = email.split('@')[0]
    # Remove any special characters, keep only alphanumeric and underscore
    username = re.sub(r'[^a-zA-Z0-9_]', '_', username)
    return username.lower()

# Track active synthesis processes per user to enable cancellation
active_synthesis_tasks = {}

PRODUCTION_ORIGINS = [
    "*",  # Allow all for dev
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]


app = FastAPI(middleware=[
    Middleware(
        CORSMiddleware,
        allow_origins=PRODUCTION_ORIGINS,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization"],
        allow_credentials=False,
        max_age=300
    )
])

# os.makedirs("static", exist_ok=True)
# app.mount("/api/static", StaticFiles(directory="static"), name="static")

# os.makedirs("accent_lib", exist_ok=True)
# app.mount("/accent_lib", StaticFiles(directory="accent_lib"), name="accent_lib")

os.makedirs("static", exist_ok=True)
os.makedirs("accent_lib", exist_ok=True)

app.mount("/api/static", StaticFiles(directory="static"), name="static")
app.mount("/accent_lib", StaticFiles(directory="accent_lib"), name="accent_lib")



@app.post("/api/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


class UserCreate(BaseModel):
    email: str
    password: str

@app.post("/api/register")
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = get_user(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user_data.password)
    db_user = User(email=user_data.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"email": db_user.email}

# Protected routes using direct app decorators
@app.get("/api/protected")
async def protected_route(user: User = Depends(validate_and_get_user)):
    """Example protected endpoint"""
    return {
        "message": "This is a protected route",
        "user_email": user.email
    }

@app.get("/api/users/me")
async def get_current_user(user: User = Depends(validate_and_get_user)):
    """Get current user details"""
    return {
        "email": user.email,
        "is_active": user.is_active
        # Include other user fields as needed
    }


@app.post("/api/translate/")
async def translateAndtranscribe_audio(
    user_email: str = Form(...),
    file: UploadFile = File(...),
    source_lang: str = Form("auto"),
    target_lang: str = Form("fra_Latn"),
    enhance_audio_flag: bool = Form(False)
):
    print("Processing audio")
    # Define paths using username
    username = email_to_username(user_email)
    user_dir = f"static/{username}"
    UPLOAD_PATH = f"{user_dir}/original.wav"
    ENHANCED_PATH = f"{user_dir}/enhanced.wav"
    os.makedirs(user_dir, exist_ok=True)
    if os.path.exists(user_dir):
        for f in os.listdir(user_dir):
            try:
                os.remove(os.path.join(user_dir, f))
            except:
                pass

    # Save uploaded audio
    with open(UPLOAD_PATH, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Denoise audio if enabled (using Resemble Enhance)
    print("🎵 Audio denoising enabled (Resemble Enhance)")
    audio_for_processing = denoise_audio(UPLOAD_PATH, ENHANCED_PATH)
    
    # 🚨 FIX: Use Google Speech Recognition for Hindi
        # 🚨 FIX: Use Google Speech Recognition for Hindi
    if source_lang == "hin_Deva":
        print(f"🔊 USING GOOGLE SPEECH RECOGNITION FOR HINDI")
        
        # Convert audio to proper WAV format for Google Speech Recognition
        CONVERTED_PATH = f"{user_dir}/converted.wav"
        try:
            # First convert to proper WAV format that Google can read
            subprocess.run([
                'ffmpeg', '-i', UPLOAD_PATH, 
                '-acodec', 'pcm_s16le', 
                '-ar', '16000', 
                '-ac', '1', 
                '-f', 'wav',  # Force WAV format
                CONVERTED_PATH, 
                '-y'
            ], check=True, capture_output=True)
            
            # Verify the file was created and has content
            if os.path.exists(CONVERTED_PATH) and os.path.getsize(CONVERTED_PATH) > 0:
                audio_for_processing = CONVERTED_PATH
                print("✅ Audio converted for Google Speech Recognition")
            else:
                raise Exception("Converted file is empty or doesn't exist")
                
        except Exception as e:
            print(f"❌ Audio conversion failed: {e}")
            print("🔄 Using original audio with Whisper")
            audio_for_processing = UPLOAD_PATH
            text = transcribe(audio_for_processing, language="hi")
        else:
            # Use Google for Hindi transcription
            from pipeline.transcriber import transcribe_hindi
            text = transcribe_hindi(audio_for_processing)
            
            # If Google fails, fall back to Whisper
            if not text:
                print("🔄 Google failed, falling back to Whisper Hindi")
                text = transcribe(audio_for_processing, language="hi")
            
    elif source_lang != "auto":
        source_lang_whisper = nllb_to_whisper_lang_code(source_lang.split('_')[0])
        text = transcribe(audio_for_processing, language=source_lang_whisper)
    else:
        # Auto-detect language
        text = transcribe(audio_for_processing)
    # Clean transcription text
    text = clean_transcription(text)
    print(f"📝 Cleaned transcription: {text[:100]}...")

    # Translate
    translated = translate(text, source_lang, target_lang) if source_lang != target_lang else text
    
    # Clean translation text
    translated = clean_translation(translated)
    print(f"📝 Cleaned translation: {translated[:100]}...")

    return {
        "transcription": text,
        "translation": translated,
        "original_audio": ENHANCED_PATH,
        "enhanced_audio": audio_for_processing if enhance_audio_flag else None,
        "enhancement_used": enhance_audio_flag
    }


@app.post("/api/cloneaudio/")
async def clone_audio(
    request: Request,
    translated_text: str = Form(...),
    transcription: str = Form(""),  # Original transcription text
    user_email: str = Form(...),
    target_lang: str = Form("fra_Latn"),
    use_saved_accent: bool = Form(False),  # Whether to use saved accent
    saved_accent_id: Optional[int] = Form(None),  # ID of saved accent to use
    db: Session = Depends(get_db)
):
    print(f"🎙️ TTS Request for {user_email}")
    print(f"   Translated: {translated_text}")
    print(f"   Target lang: {target_lang}")
    print(f"   Use saved accent: {use_saved_accent}")
    print(f"   Saved accent ID: {saved_accent_id}")

    # Mark this user as having an active synthesis task
    active_synthesis_tasks[user_email] = True

    try:
        # Check if client disconnected
        if await request.is_disconnected():
            print(f"❌ Client disconnected for {user_email}, aborting synthesis")
            raise HTTPException(status_code=499, detail="Client disconnected")

        # Synthesize speech using username for paths
        username = email_to_username(user_email)
        user_dir = f"static/{username}"
        os.makedirs(user_dir, exist_ok=True)

        # Final output path
        GENERATED_AUDIO_PATH = f"{user_dir}/generated_audio.wav"

        # Convert language code
        # DIRECT LANGUAGE MAPPING - Add this
        lang_mapping = {
            'eng_Latn': 'en', 'hin_Deva': 'hi', 'spa_Latn': 'es', 'fra_Latn': 'fr',
            'deu_Latn': 'de', 'jpn_Jpan': 'ja', 'kor_Hang': 'ko', 'zho_Hans': 'zh',
            'arb_Arab': 'ar', 'ita_Latn': 'it', 'por_Latn': 'pt', 'rus_Cyrl': 'ru',
            'ben_Beng': 'bn', 'tam_Taml': 'ta', 'tel_Telu': 'te', 'kan_Knda': 'kn',
            'mal_Mlym': 'ml', 'pan_Guru': 'pa', 'urd_Arab': 'ur', 'mar_Deva': 'mr',
            'guj_Gujr': 'gu', 'nld_Latn': 'nl'
        }

        whisper_lang = lang_mapping.get(target_lang, 'en')
        print(f"🌐 DIRECT LANGUAGE MAPPING: {target_lang} -> {whisper_lang}")

        # FORCE DEFAULT VOICE WHEN NO ACCENT SELECTED
        if use_saved_accent and saved_accent_id:
            # Use saved accent from database
            user = get_user(db, user_email)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            accent = db.query(SavedAccent).filter(
                SavedAccent.id == saved_accent_id,
                SavedAccent.user_id == user.id
            ).first()

            if not accent:
                raise HTTPException(status_code=404, detail="Saved accent not found")

            speaker_wav = accent.file_path
            speaker_text = "accent reference audio"
            print(f"🎭 Using SAVED ACCENT: {accent.accent_name}")
            
            # Generate speech with F5-TTS (voice cloning)
            print(f"🎤 Starting F5-TTS VOICE CLONING...")
            status = synthesize(
                text=translated_text,
                speaker_text=speaker_text,
                speaker_wav=speaker_wav,
                output_path=GENERATED_AUDIO_PATH,
                lang=whisper_lang,
                model="f5tts"
            )
            
        else:
            # FORCE DEFAULT SYSTEM VOICE - NO VOICE CLONING
            print(f"🔊 FORCING DEFAULT SYSTEM VOICE - No voice cloning")
            
            # Generate speech with DEFAULT VOICE (no speaker_wav)
            status = synthesize(
                text=translated_text,
                speaker_text="",
                speaker_wav="",  # EMPTY = default voice
                output_path=GENERATED_AUDIO_PATH,
                lang=whisper_lang,
                model="gtts"  # Force gTTS for default voice
            )

        # Check if client disconnected after TTS
        if await request.is_disconnected():
            print(f"❌ Client disconnected for {user_email}, aborting")
            raise HTTPException(status_code=499, detail="Client disconnected")

        print(f"✅ Synthesis complete for {user_email}")
        return {
            "translated_audio": f"api/static/{username}/generated_audio.wav",
            "synthesis_status": status,
            "model_used": status.get("model", "unknown"),
            "voice_used": "saved_accent" if use_saved_accent else "default_system_voice"
        }
    finally:
        # Always clean up the active task marker
        if user_email in active_synthesis_tasks:
            del active_synthesis_tasks[user_email]
            print(f"🧹 Cleaned up synthesis task for {user_email}")


@app.post("/api/accent_upload/")
async def process_audio(
    user_email: str= Form(...),
    file: UploadFile = File(...),
    lang: str = Form("auto")
):
    print("Processing audio for accent library")
    username = email_to_username(user_email)
    lang = nllb_to_whisper_lang_code(lang.split('_')[0])
    lib_path = f"accent_lib/{username}"
    os.makedirs(lib_path, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        tmp.write(file.file.read()); tmp.flush()
        clip_audio(tmp.name, f"{lib_path}/_{lang}.wav")

    return {
        "status": 'Accent audio saved successfully',
        "file_path": f"accent_lib/{username}/_{lang}.wav"
    }



@app.get("/api/accent_languages")
async def list_user_languages(user_email: str = Query(...)):
    username = email_to_username(user_email)
    user_dir = f"accent_lib/{username}"

    if not os.path.isdir(user_dir):
        return []

    audio_files = [
        {
            "lang": f.split("_")[-1].split(".")[0],
            "url": f"accent_lib/{username}/{f}"
        }
        for f in os.listdir(user_dir)
        if f.endswith(".wav")
    ]
    return audio_files

@app.post("/api/save_accent/")
async def save_accent(
    user_email: str = Form(...),
    accent_name: str = Form(...),
    file: UploadFile = File(...),
    lang: str = Form(...),
    db: Session = Depends(get_db)
):
    print("Received Accent:", user_email, accent_name, lang, file.filename, file.content_type)
    """Save accent audio with user-provided name"""
    # Get user from database
    user = get_user(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create user accent directory using username
    username = email_to_username(user_email)
    lang_code = nllb_to_whisper_lang_code(lang.split('_')[0])
    accent_dir = f"accent_lib/{username}/saved_accents"
    os.makedirs(accent_dir, exist_ok=True)

    # Generate unique filename
    import time
    timestamp = int(time.time())
    filename = f"{accent_name.replace(' ', '_')}_{lang_code}_{timestamp}.wav"
    file_path = f"{accent_dir}/{filename}"

    # Save audio file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        tmp.write(file.file.read())
        tmp.flush()
        clip_audio(tmp.name, file_path)

    whisper_lang = nllb_to_whisper_lang_code(lang.split('_')[0])
    print(f"🌐 Language conversion: {lang} -> {whisper_lang}")

    # Save to database
    saved_accent = SavedAccent(
        user_id=user.id,
        accent_name=accent_name,
        language_code=whisper_lang,
        file_path=file_path
    )
    db.add(saved_accent)
    db.commit()
    db.refresh(saved_accent)

    return {
        "status": "success",
        "accent_id": saved_accent.id,
        "accent_name": accent_name,
        "file_path": file_path
    }

@app.get("/api/saved_accents/")
async def get_saved_accents(
    user_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get list of saved accents for a user"""
    user = get_user(db, user_email)
    if not user:
        return []

    accents = db.query(SavedAccent).filter(SavedAccent.user_id == user.id).all()

    return [
        {
            "id": accent.id,
            "name": accent.accent_name,
            "language": accent.language_code,  # ✅ This will now be "hi" instead of "hin_Deva"
            "file_path": accent.file_path,
            "created_at": accent.created_at.isoformat()
        }
        for accent in accents
    ]

@app.delete("/api/saved_accent/{accent_id}")
async def delete_saved_accent(
    accent_id: int,
    user_email: str = Query(...),
    db: Session = Depends(get_db)
):
    """Delete a saved accent"""
    user = get_user(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    accent = db.query(SavedAccent).filter(
        SavedAccent.id == accent_id,
        SavedAccent.user_id == user.id
    ).first()

    if not accent:
        raise HTTPException(status_code=404, detail="Accent not found")

    # Delete file
    if os.path.exists(accent.file_path):
        os.remove(accent.file_path)

    # Delete from database
    db.delete(accent)
    db.commit()

    return {"status": "success", "message": "Accent deleted"}

@app.get("/api/audio")
def get_output_audio(user_email: str = Query(...)):
    TTS_PATH = f"static/{user_email}/tts.wav"
    return FileResponse(TTS_PATH, media_type="audio/wav")


@app.get("/api/ping")
def ping():
    return {"status":"OK"}
