from langchain.agents import Tool, initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories.file import FileChatMessageHistory
from langchain_core.messages import SystemMessage
from app.db.mongo import MongoChatMessageHistory
from langchain.prompts import MessagesPlaceholder
from app.core.prompts import SYSTEM_PROMPT
from app.core.tools import (
  buscar_nombre_cliente
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
    Tool.from_function(buscar_nombre_cliente, name="buscar_nombre_cliente", description="Busca el nombre completo de un cliente en Supabase usando coincidencia parcial en la columna full_name. El input es parte o todo el nombre del cliente."),
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
