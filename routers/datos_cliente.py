import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from datetime import datetime
from return_codes import *
from jwt_manager import JWTBearer

max_length_id_cliente = 11

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
consulta_datos_cliente_router = APIRouter()



@consulta_datos_cliente_router.get("/consulta_datos_cliente", tags=['Base_de_datos_UL'], status_code=200, dependencies=[Depends(JWTBearer())])
def consulta_datos_cliente(ID_CLIENTE: int):
    """
    ## **Descripción:**
    Esta función retorna los siguientes datos de un cliente en específico: ID_CLIENTE, IDENTIFICACION, TIPO_IDENTIFICACION, NOMBRE_CLIENTE, NOMBRE_CHATBOT, URL_SCRIPT, MANEJO_VOZ 
    , TELEFONO, URL_LOGO, CORREO_SOPORTE, MENSAJE_CORREO, URL_CHATBOT, REPRESENTANTE, CARGO_REPRESENTANTE y NOMBRE_PLANTILLA. 

    ## **Parámetros obligatorios:**
        - ID_CLIENTE -> ID del cliente en la base de datos UL.
        
    ## **Códigos retornados:**
        - 200 -> Registros encontrados.
        - 452 -> No se encontró información sobre ese id en la base de datos.

    ## **Campos retornados:**
        - ID_CLIENTE -> ID del cliente.
        - IDENTIFICACION -> Número de identificación del cliente.
        - TIPO_IDENTIFICACION -> Tipo de identificación del cliente. NIT, RUT
        - NOMBRE_CLIENTE -> Nombre del cliente.
        - NOMBRE_CHATBOT -> Nombre del chatbot del cliente.
        - URL_SCRIPT -> URL del chatbot del cliente.
        - MANEJO_VOZ -> Estado de activación del servicio de voz. 1=True, 0=False
        - TELEFONO -> Teléfono del cliente.
        - URL_LOGO -> URL del logo del cliente.
        - CORREO_SOPORTE -> Correo de soporte del cliente.
        - MENSAJE_CORREO -> Mensaje en formato html para el cuerpo del correo enviado con la cotización.
        - URL_CHATBOT -> URL de la página donde esta alojado el chatbot.
        - REPRESENTANTE -> Nombre completo del representante del cliente.
        - CARGO_REPRESENTANTE -> Cargo del representante del cliente.
        - NOMBRE_PLANTILLA -> Nombre de la plantilla para las cotizaciones.
    """
    with engine.connect() as connection:
        consulta_sql = text("""
            SELECT * FROM CLIENTE c WHERE c.ID_CLIENTE = :ID_CLIENTE;
        """).params(ID_CLIENTE=ID_CLIENTE)
        result = connection.execute(consulta_sql)
        rows = result.fetchall()
        column_names = result.keys()

        result_dicts = []
        for row in rows:
            row_dict = dict(zip(column_names, row))
            result_dicts.append(row_dict)

        if result_dicts:
            return JSONResponse(content=result_dicts)
        else:
            codigo = SIN_INFORMACION
            mensaje = HTTP_MESSAGES.get(codigo)
            raise HTTPException(codigo, mensaje)
