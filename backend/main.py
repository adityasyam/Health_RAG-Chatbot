from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from conversation import generate_chat_response, update_conversation_context
from voice import speech_to_text, text_to_speech
import re
import os
import logging
import traceback
import pdfplumber  

# logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/voice")
async def process_voice_input(audio_file: UploadFile = File(...)):
    try:
        # Log file info
        logger.info(f"Received audio file: {audio_file.filename}")
        logger.info(f"Content type: {audio_file.content_type}")

        # Validating file type
        allowed_types = ['audio/wav', 'audio/mp3', 'audio/mpeg']
        if audio_file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {audio_file.content_type}")

        # Converting speech to text
        transcribed_text = await speech_to_text(audio_file)
        logger.info(f"Transcribed text: {transcribed_text}")

        # Generating chat response
        chat_response = generate_chat_response(transcribed_text)
        logger.info(f"Chat response: {chat_response}")

        # Converting response to speech
        output_file = "response.wav"
        await text_to_speech(chat_response, output_file)
        
        # Returning the audio file to be played 
        return FileResponse(output_file, media_type="audio/wav")
    
    except Exception as e:
        # Logging full error details
        logger.error(f"Voice processing error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Raising HTTP exception
        raise HTTPException(
            status_code=500, 
            detail=f"Detailed voice processing error: {str(e)}"
        )


class ChatRequest(BaseModel):
    user_query: str

def parse_patient_record(content: str) -> dict:
    try:
        # Extracting patient number
        patient_num_match = re.search(r'#(\d+)', content)
        patient_num = patient_num_match.group(1) if patient_num_match else "Unknown"

        # Extracting past history
        past_history_match = re.search(r'Past history\s*-\s*(.+?)(?:Family history|$)', content, re.IGNORECASE | re.DOTALL)
        past_history = past_history_match.group(1).strip() if past_history_match else ""

        # Extracting family history
        family_history_match = re.search(r'Family history\s*-\s*(.+)', content, re.IGNORECASE | re.DOTALL)
        family_history = family_history_match.group(1).strip() if family_history_match else ""

        return {
            "patient_number": patient_num,
            "past_history": [condition.strip() for condition in past_history.split(',')],
            "family_history": [condition.strip() for condition in family_history.split(',')]
        }
    except Exception as e:
        raise ValueError(f"Error parsing patient record: {str(e)}")


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        #Generating chat response
        response = generate_chat_response(request.user_query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-record")
async def upload_record(file: UploadFile = File(...)):
    try:
        # Read file content
        content_type = file.content_type
        if content_type == "text/plain":
            content = await file.read()
            content_str = content.decode('utf-8')
        elif content_type == "application/pdf":
            # with pdfplumber.open(file.file) as pdf:
            #     content_str = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
            if content_type == "application/pdf":
                with pdfplumber.open(file.file) as pdf:
                    content_str = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
                print("Extracted PDF Content:", content_str)  # Debugging
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")
        
        # Parse the patient record
        patient_data = parse_patient_record(content_str)
        
        # Update the conversation context with the patient data
        update_conversation_context(patient_data)
        
        # Generate initial response about risk factors
        query = f"Based on the patient #{patient_data['patient_number']}'s past history of {', '.join(patient_data['past_history'])} "\
                f"and family history of {', '.join(patient_data['family_history'])}, what other diseases might they be at risk for?"
        
        response = generate_chat_response(query)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice")
async def process_voice_input(audio_file: UploadFile = File(...)):
    try:
        # Converting speech to text
        transcribed_text = await speech_to_text(audio_file)
        
        # Generating chat response
        chat_response = generate_chat_response(transcribed_text)
        
        # Converting response to speech
        output_file = "response.wav"
        await text_to_speech(chat_response, output_file)
        
        # Returning the audio file to be played
        return FileResponse(output_file, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")
