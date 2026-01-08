import google.generativeai as genai
import os
from dotenv import load_dotenv
# load_dotenv()
# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key='AIzaSyAZRZO9S6ouDGKnGqOks6jo9onz9ggWJGI')

# List available models
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(model.name)