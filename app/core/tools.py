# app/core/tools.py

from langchain.tools import tool
from app.data.questions import question_list
from app.db.respositories import PostgresDB
import time
import re
import os
from app.db.supabase import get_supabase_client

user_state = {field: None for field, _ in question_list}


@tool
def get_next_question(input: str) -> str:
    """Devuelve la siguiente pregunta pendiente para completar el flujo."""
    for field, question in question_list:
        if not user_state.get(field):
            return question
    return "¡Gracias! Ya tenemos toda la información necesaria. Un asesor te contactará pronto."




@tool
def buscar_nombre_cliente(input: str) -> str:
    """Busca clientes en Supabase por coincidencia parcial en el nombre (full_name) y muestra nombre, email y teléfono."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("clients").select("full_name, email, phone").ilike("full_name", f"%{input}%").execute()
        if response.data and len(response.data) > 0:
            resultados = []
            for cliente in response.data:
                nombre = cliente.get("full_name", "Sin nombre")
                email = cliente.get("email", "Sin email")
                phone = cliente.get("phone", "Sin teléfono")
                resultados.append(f"Nombre: {nombre}\nEmail: {email}\nTeléfono: {phone}")
            return "Clientes encontrados:\n\n" + "\n---\n".join(resultados)
        return "No se encontró ningún cliente con ese nombre."
    except Exception as e:
        return f"Error al buscar el cliente en Supabase: {e}"
    
    

