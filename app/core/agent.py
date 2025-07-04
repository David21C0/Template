from langchain.agents import Tool, initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories.file import FileChatMessageHistory
from langchain_core.messages import SystemMessage
from app.db.mongo import MongoChatMessageHistory
from langchain.prompts import MessagesPlaceholder
from app.core.prompts import SYSTEM_PROMPT
from app.core.tools import (
    proyecto_por_distrito,
    detalles_proyecto,
    propiedades_disponibles,
    precio_propiedades,
    imagenes_proyecto_zonas_comunes,
    imagenes_propiedades,
    obtener_proyectos
)
import os
import json

from dotenv import load_dotenv

load_dotenv()


llm = ChatOpenAI(
    temperature=0.3,
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)
#TODO: Baja prioridad, validar si puede ejecutar varios tools a la vez, por ejemplo si el usuario pide ver los departamentos y las zonas comunes, que pueda ejecutar ambas tools y no una sola.
tools = [
    Tool.from_function(proyecto_por_distrito, name="proyecto_por_distrito", description="Informacion basica de proyecto filtrado por distrito."),
    Tool.from_function(detalles_proyecto, name="detalles_proyecto", description="Detalles del proyecto y mas informacion filtrado por nombre del proyecto."),
    Tool.from_function(propiedades_disponibles, name="propiedades_disponibles", description="Propiedades por proyecto se filtra por nombre del proyecto."),
    Tool.from_function(precio_propiedades, name="precio_propiedades", description="Detalle de precios y promociones de propiedades se filtra por nombre del proyecto."),
    Tool.from_function(imagenes_proyecto_zonas_comunes, name="imagenes_proyecto_zonas_comunes", description="Imágenes de las zonas comunes del proyecto se filtra por nombre del proyecto."),
    Tool.from_function(imagenes_propiedades, name="imagenes_propiedades", description="Imágenes de propiedades el unico filtro que contiene es por nombre del proyecto y deveulve todas las imagenes de las propiedades asociadas."),
    Tool.from_function(obtener_proyectos, name="obtener_proyectos", description="Proyectos sin distrito específico para mostrar todas los proyecto disponibles y en que distritos.")
]

def get_agent(phone: str):
    print("telefono entrante", phone)
    mongo_history = MongoChatMessageHistory(phone=phone)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        chat_memory=mongo_history
    )

    agent_kwargs = {
        "extra_prompt_messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history")
        ]
    }

    return initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        memory=memory,
        agent_kwargs=agent_kwargs
    )
