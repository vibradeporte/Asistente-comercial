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
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Crear el enrutador de FastAPI
insert_datos_usuarios_router = APIRouter()



@insert_datos_usuarios_router.get("/insert_datos_usuarios", tags=['Base_de_datos_UL'], status_code=200, dependencies=[Depends(JWTBearer())])
def insert_datos_usuarios(NOMBRE_COMPLETO: str = Query(...), CORREO: str = Query(...), WHATSAPP: str = Query(...), TIPO_USUARIO: str = Query(...), EMPRESA: str = Query(...), 
                          CARGO: str = Query(...)):
    """
    ## **Descripción:**
    Esta función permite insertar en la base de datos los valores ingresados por el usuario en la conversación.

    ## **Parámetros obligatorios:**
        - NOMBRE_COMPLETO -> Nombre completo del usuario.
        - CORREO -> Correo electrónico ingresado por el usuario.
        - WHATSAPP -> Número celular ingresado por el usuario.
        - TIPO_USUARIO -> Tipo de usuario. P->Particular. E->empresa.
        - EMPRESA -> Empresa ingresada por el usuario. Sí es una persona particular la empresa será "particular".
        - CARGO -> Cargo del usuario dentro de la empresa. Sí es una persona particular el cargo será "particular".
        
    ## **Códigos retornados:**
        - 200 -> Registros encontrados.

    """
    with engine.connect() as connection:
        consulta_sql = text("""
            insert into USUARIO (NOMBRE_COMPLETO, CORREO, WHATSAPP, TIPO_USUARIO,EMPRESA,CARGO) VALUES (:NOMBRE_COMPLETO,:CORREO,:WHATSAPP,:TIPO_USUARIO,:EMPRESA,:CARGO)
        """).params(NOMBRE_COMPLETO=NOMBRE_COMPLETO,CORREO=CORREO,WHATSAPP=WHATSAPP,TIPO_USUARIO=TIPO_USUARIO,EMPRESA=EMPRESA,CARGO=CARGO)
        try:
            result = connection.execute(consulta_sql)
            connection.commit()
            ID_USUARIO = result.lastrowid
            return JSONResponse(status_code=200, content={'ID_USUARIO': ID_USUARIO})
        except Exception as e:
            return e
