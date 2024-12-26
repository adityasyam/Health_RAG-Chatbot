import os
import logging
import assemblyai as aai
from dotenv import load_dotenv
from gtts import gTTS  # Alternative TTS library

# Configuring logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# AssemblyAI Configuration
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
transcriber = aai.Transcriber()

async def speech_to_text(audio_file):
    try:
        # Save uploaded file to a temporary file
        temp_file_path = f"temp_audio_{audio_file.filename}"
        
        # Ensure the file is saved
        with open(temp_file_path, "wb") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
        
        logger.info(f"Saved temporary audio file: {temp_file_path}")
        logger.info(f"File size: {os.path.getsize(temp_file_path)} bytes")
        
        # Transcribe the file
        transcript = transcriber.transcribe(temp_file_path)
        
        # Clean up temp file
        os.remove(temp_file_path)
        
        # Checking transcript validity
        if not transcript or not transcript.text:
            raise ValueError("No text could be transcribed from the audio")
        
        logger.info(f"Transcribed text: {transcript.text}")
        return transcript.text
    
    except Exception as e:
        logger.error(f"Speech-to-text error: {str(e)}")
        raise

async def text_to_speech(text: str, output_file: str = "response.wav", language: str = 'en'):
    """
    Convert text to speech using gTTS and save to a file.
    """
    try:
        # Validate input text
        if not text or not isinstance(text, str):
            raise ValueError("Invalid text input for text-to-speech")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        
        # Create gTTS object
        tts = gTTS(text=text, lang=language)
        
        # Save to file
        tts.save(output_file)
        
        # Verify file was created
        if not os.path.exists(output_file):
            raise IOError("Failed to create speech output file")
        
        logger.info(f"Speech saved to {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Text-to-speech error: {str(e)}")
        raise
