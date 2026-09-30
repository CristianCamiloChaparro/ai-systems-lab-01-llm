"""Pruebas sin red gracias a FakeLLMClient.  Ejecutar:  uv run pytest labs/01-llm"""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fake_llm_client import FakeLLMClient  # noqa: E402
from prompts import SYSTEM_PROMPT, build_messages  # noqa: E402
from structured import analyze_question  # noqa: E402


def test_build_messages_orden_system_historial_usuario():
    history = [
        {"role": "user", "content": "Explica qué es el positional encoding"},
        {"role": "assistant", "content": "Es ..."},
    ]
    messages = build_messages(history, "Dame un ejemplo de eso")
    assert messages[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert messages[1:3] == history
    assert messages[-1] == {"role": "user", "content": "Dame un ejemplo de eso"}
    assert len(history) == 2  # no modifica el historial recibido


def test_build_messages_sin_historial():
    messages = build_messages([], "Hola")
    assert [m["role"] for m in messages] == ["system", "user"]


def test_analyze_question_conocimiento_general():
    analysis = analyze_question(FakeLLMClient(), "¿Qué es el mecanismo de atención?")
    assert analysis.requiere_documentos_del_curso is False


def test_analyze_question_informacion_del_curso():
    analysis = analyze_question(FakeLLMClient(), "¿Qué temas entran en el parcial?")
    assert analysis.requiere_documentos_del_curso is True
    assert analysis.respuesta_corta == "No tengo esa información"


def test_analyze_question_rechaza_valor_fuera_del_esquema():
    bad = '{"tema": "x", "dificultad": "media", "requiere_documentos_del_curso": false, "respuesta_corta": "y"}'
    with pytest.raises(ValidationError):
        analyze_question(FakeLLMClient(responses=[bad]), "cualquier pregunta")


def test_analyze_question_rechaza_json_invalido():
    import json

    with pytest.raises(json.JSONDecodeError):
        analyze_question(FakeLLMClient(responses=["esto no es JSON"]), "cualquier pregunta")
