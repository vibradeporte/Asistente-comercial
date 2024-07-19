import base64
import os
import requests
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List
from jwt_manager import JWTBearer
from jwt_manager import JWTBearer

max_length_correo = 80

class AttachmentSchema(BaseModel):
    content: str
    name: str
    type: str

class EmailSchema(BaseModel):
    from_e: str = Field(..., max_length=max_length_correo)
    to: str = Field(..., max_length=max_length_correo)
    subject: str
    html_content: str
    content: str
    attachments: List[AttachmentSchema] = []

load_dotenv()
AUTH_KEY = os.getenv("AUTH_KEY")
API_URL = "https://api.turbo-smtp.com/api/v2/mail/send"
AUTH_USER_TSMTP = os.getenv("AUTH_USER_TSMTP")
AUTH_PASS_TSMTP = os.getenv("AUTH_PASS_TSMTP")

correo_router = APIRouter()

@correo_router.post("/send_email", status_code=200, dependencies=[Depends(JWTBearer())])
async def send_email(
    from_e: str = Query(..., max_length=max_length_correo),
    to: str = Query(..., max_length=max_length_correo),
    subject: str = Query(...),
    html_content: str = Query(...),
    file_url: str = Query(...)
):
    try:
        # Descargar el archivo desde la URL
        file_response = requests.get(file_url)
        if file_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Error al descargar el archivo desde la URL proporcionada.")
        
        file_content = file_response.content
        base64_encoded = base64.b64encode(file_content).decode('utf-8')

        file_name = file_url.split("/")[-1]
        file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if file_name.endswith(".docx") else "application/octet-stream"
        
        # Crear el objeto de correo electrónico
        email = EmailSchema(
            from_e=from_e,
            to=to,
            subject=subject,
            html_content=html_content,
            content="Adjunto encontrarás el archivo solicitado.",
            attachments=[AttachmentSchema(content=base64_encoded, name=file_name, type=file_type)]
        )

        # Preparar los datos para enviar el correo
        data = {
            "authuser": AUTH_USER_TSMTP,
            "authpass": AUTH_PASS_TSMTP,
            "from": email.from_e,
            "to": email.to,
            "subject": email.subject,
            "content": email.content,
            "html_content": email.html_content,
            "attachments": [
                {
                    "content": attachment.content,
                    "name": attachment.name,
                    "type": attachment.type
                } for attachment in email.attachments
            ]
        }

        headers = {
            'Authorization': AUTH_KEY
        }

        # Realizar la petición POST a la API de turboSMTP
        response = requests.post(API_URL, headers=headers, json=data)
        if response.status_code == 200:
            return {"message": "Correo enviado exitosamente."}
        else:
            # En caso de error, retorna un mensaje con el código de estado y el error
            raise HTTPException(response.status_code, response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
