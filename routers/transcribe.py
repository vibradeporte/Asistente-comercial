from fastapi import APIRouter, FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from jwt_manager import JWTBearer
import requests
import time
import os

load_dotenv()
transcribe_app = APIRouter()




Authorization = os.getenv("OPENAI_API_KEY")


@transcribe_app.post("/transcribe/", dependencies=[Depends(JWTBearer())])
async def transcribe_audio(file: UploadFile = File(...)):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {Authorization}"
    }
    data = {
        "model": "whisper-1", 
        "language": "es"
    }

    start_time = time.time()
    response = requests.post(
        url, headers=headers, files={"file": (file.filename, await file.read(), "audio/mp3")}, data=data)
    end_time = time.time()

    if response.status_code == 200:
        elapsed_time = end_time - start_time
        return {
            "transcription": response.json(),
            "elapsed_time": elapsed_time
        }
    else:
        raise HTTPException(
            status_code=response.status_code, detail=response.text)
