"""Offline tests for Gemini conversation continuity."""

from types import SimpleNamespace

from ayeon.gemini_generator import GeminiChatGenerator


def test_gemini_chat_reuses_one_session_for_multiple_messages() -> None:
    messages = []
    creations = []

    class FakeChat:
        def send_message(self, prompt: str):
            messages.append(prompt)
            return SimpleNamespace(text="Respuesta de Ayeon.")

    class FakeChats:
        def create(self, **kwargs):
            creations.append(kwargs)
            return FakeChat()

    generator = GeminiChatGenerator(
        client=SimpleNamespace(chats=FakeChats()),
        model="gemini-3.5-flash-lite",
    )

    assert generator.generate("Mi color favorito es azul") == "Respuesta de Ayeon."
    assert generator.generate("Cual es mi color favorito?") == "Respuesta de Ayeon."
    assert messages == [
        "Mi color favorito es azul",
        "Cual es mi color favorito?",
    ]
    assert len(creations) == 1
    assert creations[0]["model"] == "gemini-3.5-flash-lite"
    assert "Ayeon" in creations[0]["config"].system_instruction
