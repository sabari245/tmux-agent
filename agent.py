from typing import Any, Dict
from typing_extensions import TypedDict
import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

load_dotenv(".env.local")


class Command(TypedDict):
    command: str


def _build_agent() -> Agent[Command]:
    model = OpenAIChatModel(
        "openai/gpt-4.1-mini",
        provider=OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY")),
    )
    system_prompt = (
        "You are a terminal command generator.",
        "Given the user's request, tmux pane history, and system information,",
        "produce a single shell command that best accomplishes the request.",
        "Return only the command in the `command` field. No explanations.",
    )
    return Agent(system_prompt=system_prompt, model=model, output_type=Command)


def _format_input(
    prompt: str, tmux_history: str | None, system_info: Dict[str, Any]
) -> str:
    parts: list[str] = []
    if tmux_history:
        parts.append("<TMUX_HISTORY>")
        parts.append(tmux_history)
        parts.append("</TMUX_HISTORY>")
    parts.append("<SYSTEM_INFO>")
    for k, v in system_info.items():
        parts.append(f"{k}: {v}")
    parts.append("</SYSTEM_INFO>")
    parts.append("<PROMPT>")
    parts.append(prompt)
    parts.append("</PROMPT>")
    return "\n".join(parts)


def generate_command(
    prompt: str, tmux_history: str | None, system_info: Dict[str, Any]
) -> str:
    agent = _build_agent()
    user_input = _format_input(prompt, tmux_history, system_info)
    result = agent.run_sync(user_input)
    return result.output["command"].strip()
