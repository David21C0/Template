# app/core/tools.py

from langchain.tools import tool
from app.data.questions import question_list
from app.db.respositories import PostgresDB
import time
import re

user_state = {field: None for field, _ in question_list}


@tool
def get_next_question(input: str) -> str:
    """Devuelve la siguiente pregunta pendiente para completar el flujo."""
    for field, question in question_list:
        if not user_state.get(field):
            return question
    return "¡Gracias! Ya tenemos toda la información necesaria. Un asesor te contactará pronto."


@tool
def obtener_proyectos(input: str) -> str:
    """Devuelve una lista de proyectos disponibles sin especificar distrito."""
    db = PostgresDB()
    resultado = db.execute_without_param("obtener_proyectos")
    if isinstance(resultado, str):
        return resultado
    if not resultado:
        return "No se encontraron proyectos sin distrito específico."
    proyectos = []
    for p in resultado:
        nombre = p.get("name", "Sin nombre")
        proyectos.append(f"🏗️ *{nombre}*")
        distrito = p.get("district", "Sin distrito")
        proyectos.append(f"📍 {distrito}")
    return proyectos

@tool
def proyecto_por_distrito(input: str) -> str:
    """Busca proyectos disponibles en un distrito específico solo si se tiene el distrito claro."""
    distrito = re.sub(r"\s+", " ", input).strip().lower()
    db = PostgresDB()
    resultado = db.execute_single_param(distrito, "proyectos_por_distrito")

    if isinstance(resultado, str):
        return resultado

    if not resultado:
        return f"No se encontraron proyectos en {distrito.title()}."

    proyectos = []
    for p in resultado:
        nombre = p.get("name", "Sin nombre")
        descripcion = p.get("descripcion", "Sin descripción")[:150] + "..."
        direccion = p.get("address", "Sin dirección")
        reference = p.get("reference", "Sin referencia")

        proyectos.append(
            f"🏗️ *{nombre}*\n📍 {direccion}\n📝 {descripcion} \n📄 {reference}"
        )

    time.sleep(1)

    return f"🔍 Proyectos encontrados en {distrito.title()}:\n\n" + "\n---\n".join(proyectos)


@tool
def detalles_proyecto(input: str) -> str:      
    """Devuelve detalles de un proyecto específico."""
    nombre = input.strip().lower()
    db = PostgresDB()
    resultado = db.execute_single_param(nombre, "mas_informacion_proyecto")
    if isinstance(resultado, str):
        return resultado
    if not resultado:
        return "No se encontraron detalles del proyecto."
    detalles = []
    for p in resultado:
        nombre = p.get("name", "Sin nombre")
        details = p.get("details", "Sin detalles")
        video_url = p.get("video_url", "No disponible")
        brochure_url = p.get("brochure_url", "No disponible")
        detalles.append(f"🏗️ *{nombre}*\n📝 {details} \n📄 {brochure_url} \n📺 {video_url}")
    return "\n".join(detalles)



@tool
def propiedades_disponibles(input: str) -> str: 
    """Devuelve información sobre propiedades disponibles"""
    nombre = re.sub(r"\s+", " ", input).strip().lower()
    db = PostgresDB()
    resultado = db.execute_single_param(nombre, "propiedades_disponibles_proyecto")
    if isinstance(resultado, str):
        return resultado
    if not resultado:
        return "No se encontraron propiedades disponibles en el proyecto."
    propiedades = []
    for p in resultado:
        nombre = p.get("name", "Sin nombre")
        title = p.get("title", "sin titulo")
        bedrooms = p.get("bedrooms", "sin habitaciones")
        bathrooms = p.get("bathrooms", "sin baños")
        area_m2 = p.get("area_m2", "sin area")
        description = p.get("description", "sin descripcion")
        propiedades.append(f"🏠 *{nombre}* - {title} - {bedrooms} habitaciones - {bathrooms} baños - {area_m2} m2 - {description}")
    return "\n".join(propiedades)   

@tool
def precio_propiedades(input: str) -> str:
    """Devuelve información sobre precios de propiedades."""
    nombre = re.sub(r"\s+", " ", input).strip().lower()
    db = PostgresDB()
    resultado = db.execute_single_param(nombre, "precios_promociones_propiedad")
    if isinstance(resultado, str):
        return resultado
    if not resultado:
        return "No se encontraron precios de propiedades."
    precios = []
    for p in resultado:
        name_project = p.get("name_project", "sin nombre")
        title = p.get("title", "sin titulo")
        area_m2 = p.get("area_m2", "sin area")
        price_description = p.get("price_description", "sin precio")
        promotion = p.get("promotion", "sin promocion")
        precios.append(f"🏠 *{name_project}* - {title} - {area_m2} m2 - {price_description} - {promotion}")
    return "\n".join(precios)

@tool
def imagenes_proyecto_zonas_comunes(input: str) -> str:
    """Devuelve algunas imágenes de un proyecto específico."""
    nombre = input.strip().lower()
    db = PostgresDB()
    resultado = db.execute_single_param(nombre, "imagenes_proyecto_zonas_comunes")
    if isinstance(resultado, str):
        return resultado
    if not resultado:
        return "No se encontraron imagenes de zonas comunes del proyecto."
    imagenes = []
    for p in resultado:
        type = p.get("type", "sin tipo")
        url = p.get("url", "sin url")
        imagenes.append(f"🏠 *{type}* - {url}")
    return "\n".join(imagenes)
    
    


@tool
def imagenes_propiedades(input: str) -> str:
    """Devuelve algunas fotos de propiedades disponibles."""
    nombre = re.sub(r"\s+", " ", input).strip().lower()
    db = PostgresDB()
    resultado = db.execute_single_param(nombre, "imagenes_propiedades_disponibles")
    if isinstance(resultado, str):
        return resultado
    if not resultado:
        return "No se encontraron imagenes de propiedades disponibles."
    imagenes = []
    for p in resultado:
        type = p.get("type", "sin tipo")
        url = p.get("url", "sin url")
        imagenes.append(f"🏠 *{type}* - {url}")
    return "\n".join(imagenes)
    
