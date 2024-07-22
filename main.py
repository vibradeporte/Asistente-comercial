from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from routers.transcribe import transcribe_app
from routers.userlog import userlog_router
from routers.archivo import archivo_router
from fastapi.staticfiles import StaticFiles
import requests
from routers.datos_cliente import consulta_datos_cliente_router
from routers.correos import correo_archivo_adjunto_router
from routers.insert_datos_usuario import insert_datos_usuarios_router
from routers.insert_datos_sesion import insert_datos_sesion_router


app = FastAPI()
app.title = "ASISTENTE COMERCIAL API"
app.version = "0.0.1"

app.include_router(transcribe_app)
app.include_router(userlog_router)
app.include_router(archivo_router)

app.include_router(consulta_datos_cliente_router)
app.include_router(insert_datos_usuarios_router)
app.include_router(insert_datos_sesion_router)



app.include_router(correo_archivo_adjunto_router)


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/', tags=['home'])
def message():
    response = requests.get('https://ipinfo.io/ip')
    ip_address = response.text.strip()
    print(ip_address)
    return HTMLResponse(f'<h1>Universal Learning API ASISTENTE COMERCIAL</h1><p>Client IP: {ip_address}</p>')
