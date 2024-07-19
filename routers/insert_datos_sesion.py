import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from datetime import datetime
from return_codes import *
from jwt_manager import JWTBearer


# Cargar variables de entorno
load_dotenv()
usuario = os.getenv("USER_DB_UL")
contrasena = os.getenv("PASS_DB_UL")
host = os.getenv("HOST_DB_UL")
nombre_base_datos = os.getenv("NAME_DB_UL")

# Codificar la contraseña para la URL de conexión
contrasena_codificada = quote_plus(contrasena)
DATABASE_URL = f"mysql+mysqlconnector://{usuario}:{contrasena_codificada}@{host}/{nombre_base_datos}"
engine = create_engine(DATABASE_URL)

# Crear el enrutador de FastAPI
insert_datos_sesion_router = APIRouter()



@insert_datos_sesion_router.get("/insert_datos_sesion", tags=['Base_de_datos_UL'], status_code=200, dependencies=[Depends(JWTBearer())])
def insert_datos_sesion(FECHA_HORA_INICIO: datetime = Query(...), FECHA_HORA_FIN: datetime = Query(...), FID_USUARIO: str = Query(...), FID_CLIENTE: str = Query(...), 
                        DIALOGO: str = Query(...), ESTADO_FINAL: str = Query(...), NIVEL_SATISFACCION: str = Query(...)):
    """
    ## **Descripción:**
    Esta función permite insertar en la base de datos los valores de la sesión.

    ## **Parámetros obligatorios:**
        - FECHA_HORA_INICIO -> Fecha y hora del inicio de la conversación.
        - FECHA_HORA_FIN -> Fecha y hora del fin de la conversación.
        - FID_USUARIO -> Número de identificación del usuario.
        - FID_CLIENTE -> Número de identificación del cliente.
        - DIALOGO -> Conversación completa en la sesión.
        - ESTADO_FINAL -> Estado final de la conversación. 1->Abortada(timeout). 2->Finalizada por usuario prematuramente. 3-> Finalizada con envío de cotización. 
            4-> Compra materializada. 5-> Sin interés de compra.
        - NIVEL_SATISFACCION -> Nivel de satisfacción del cliente con la conversación y las respuestas del asistente.
        
    ## **Códigos retornados:**
        - 200 -> Registros encontrados.

    """
    with engine.connect() as connection:
        consulta_sql = text("""
            insert into SESION (FECHA_HORA_INICIO, FECHA_HORA_FIN, FID_USUARIO, FID_CLIENTE, DIALOGO, ESTADO_FINAL, NIVEL_SATISFACCION) VALUES (:FECHA_HORA_INICIO, :FECHA_HORA_FIN,
                             :FID_USUARIO, :FID_CLIENTE, :DIALOGO, :ESTADO_FINAL, :NIVEL_SATISFACCION)
        """).params(FECHA_HORA_INICIO=FECHA_HORA_INICIO, FECHA_HORA_FIN=FECHA_HORA_FIN, FID_USUARIO=FID_USUARIO, FID_CLIENTE=FID_CLIENTE, DIALOGO=DIALOGO, ESTADO_FINAL=ESTADO_FINAL, NIVEL_SATISFACCION=NIVEL_SATISFACCION)
        
        try:
            result = connection.execute(consulta_sql)
            connection.commit()
            ID_SESION = result.lastrowid
            return JSONResponse(status_code=200, content={'ID_SESION': ID_SESION})
        except Exception as e:
            return e
