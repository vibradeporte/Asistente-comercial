from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from docx import Document
import os
from typing import List
from pydantic import BaseModel
import json
from jwt_manager import JWTBearer

archivo_router = APIRouter()

class Producto(BaseModel):
    cantidad: int
    producto: str
    descripcion: str
    unidad: str
    valor_unitario: str
    valor_total: str
    
class Cotizacion(BaseModel):
    fecha: str
    cliente: str
    usuario: str
    cotizacion: List[Producto]
    valor_total: str
    representante: str
    url_chatbot: str
    cargo_representante: str
    correo_soporte: str
    telefono: str
    nombre_plantilla: str


@archivo_router.post("/convert/", dependencies=[Depends(JWTBearer())])
async def convert_word(
    request: Request,
    cotizacion: Cotizacion
):
    # Parsear la cotización como una lista de productos
    productos = cotizacion.cotizacion

    # Directorio temporal y archivo fijo
    temp_dir = "static/temp_files"
    os.makedirs(temp_dir, exist_ok=True)
    input_path = os.path.join(temp_dir, f"{cotizacion.nombre_plantilla}")

    # Verificar si el archivo fijo existe
    if not os.path.exists(input_path):
        raise RuntimeError(f"El archivo fijo no existe: {input_path}")

    # Cargar el documento existente
    document = Document(input_path)

    # Reemplazar texto en párrafos
    for paragraph in document.paragraphs:
        if "FECHA" in paragraph.text:
            paragraph.text = paragraph.text.replace("FECHA", cotizacion.fecha)
        if "USUARIO" in paragraph.text:
            paragraph.text = paragraph.text.replace("USUARIO", cotizacion.usuario)
        if "VALORTOTAL" in paragraph.text:
            paragraph.text = paragraph.text.replace("VALORTOTAL", cotizacion.valor_total)
        if "CLIENTE" in paragraph.text:
            paragraph.text = paragraph.text.replace("CLIENTE", cotizacion.cliente)
        if "REPRESENTANTE" in paragraph.text:
            paragraph.text = paragraph.text.replace("REPRESENTANTE", cotizacion.representante)
        if "URL_CHATBOT" in paragraph.text:
            paragraph.text = paragraph.text.replace("URL_CHATBOT", cotizacion.url_chatbot)
        if "CARGOREPRE" in paragraph.text:
            paragraph.text = paragraph.text.replace("CARGOREPRE", cotizacion.cargo_representante)
        if "CORREO_SOPORTE" in paragraph.text:
            paragraph.text = paragraph.text.replace("CORREO_SOPORTE", cotizacion.correo_soporte)
        if "TELEFONO" in paragraph.text:
            paragraph.text = paragraph.text.replace("TELEFONO", cotizacion.telefono)

    # Buscar la tabla de cotización en el documento
    for table in document.tables:
        if "Cantidad" in table.cell(0, 0).text:
            # Borrar filas existentes excepto la cabecera
            while len(table.rows) > 1:
                table._element.remove(table.rows[-1]._element)

            # Agregar filas con datos de productos
            for producto in productos:
                row = table.add_row()
                row.cells[0].text = str(producto.cantidad)
                row.cells[1].text = producto.producto
                row.cells[2].text = producto.descripcion
                row.cells[3].text = producto.unidad
                row.cells[4].text = producto.valor_unitario
                row.cells[5].text = f"${producto.valor_total}"

    # Guardar el documento modificado
    modified_docx_path = os.path.join(temp_dir, f"cotizacion_{cotizacion.cliente}_{cotizacion.usuario}.docx")
    document.save(modified_docx_path)

    # Verificar si el documento modificado fue guardado correctamente
    if not os.path.exists(modified_docx_path):
        raise RuntimeError(f"Failed to save the modified document: {modified_docx_path}")

    # Generar la URL para la descarga del archivo
    base_url = str(request.base_url)
    download_url = os.path.join(base_url, temp_dir, os.path.basename(modified_docx_path)).replace("\\", "/")

    # Devolver la URL del archivo modificado
    response = {
        "download_url": download_url
    }

    return JSONResponse(content=response)
