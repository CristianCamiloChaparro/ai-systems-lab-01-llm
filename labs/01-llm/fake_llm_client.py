"""Proveedor falso para pruebas (reto opcional).

Implementa el mismo método `chat` que LLMClient, pero devuelve respuestas
predefinidas sin llamar a ninguna API. Se selecciona con LLM_PROVIDER=fake.
"""

import json

from config import Settings
from llm_client import LLMResponse, Message

COURSE_KEYWORDS = ("parcial", "nota", "fecha", "entrega", "programa", "horario", "examen")


class FakeLLMClient:
    def __init__(self, settings: Settings | None = None, responses: list[str] | None = None):
        self.settings = settings
        self._responses = list(responses or [])
        self.calls: list[list[Message]] = []  # para inspeccionar qué se envió en las pruebas

    def chat(
        self,
        messages: list[Message],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        self.calls.append(messages)
        question = messages[-1]["content"]
        if self._responses:
            text = self._responses.pop(0)
        elif json_mode:
            needs_docs = any(word in question.lower() for word in COURSE_KEYWORDS)
            text = json.dumps(
                {
                    "tema": "pregunta del curso" if needs_docs else "concepto general",
                    "dificultad": "basica",
                    "requiere_documentos_del_curso": needs_docs,
                    "respuesta_corta": "No tengo esa información"
                    if needs_docs
                    else "Respuesta simulada.",
                },
                ensure_ascii=False,
            )
        else:
            text = f"(respuesta simulada) Recibí {len(messages)} mensajes. Última pregunta: {question}"
        return LLMResponse(
            text=text,
            model="fake-model",
            finish_reason="stop",
            prompt_tokens=sum(len(m["content"].split()) for m in messages),
            completion_tokens=len(text.split()),
        )
