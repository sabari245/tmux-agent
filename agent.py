from pydantic_ai import Agent
from typing_extensions import TypedDict
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
import os
from dotenv import load_dotenv
from pydantic_core import to_jsonable_python
from pydantic_ai.messages import ModelMessagesTypeAdapter 
import json

load_dotenv(".env.local")


class Command(TypedDict):
    command: str

model = OpenAIChatModel(
    "openai/gpt-4.1-mini:nitro",
    provider=OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY")),
)

agent = Agent(
    system_prompt=(
        "you are a terminal command generator", 
        "when the user asks you to do something,",
        "you will return the command that is", 
        "needed to achieve the goal",
    ),
    model=model,
    output_type=Command,
)

tasks = "find the ip address of the system, hostname",

output = """
<TMUX_HISTORY>
*[main][~/code/tmux-agent]$ hostname -I
zsh: command not found: hostname
*[main][~/code/tmux-agent]$
</TMUX_HISTORY>

what should I do next?
"""

output2 = """
<TMUX_HISTORY>
*[main][~/code/tmux-agent]$ ip addr show | grep 'inet ' | awk '{print $2}' | cut -d/ -f1

127.0.0.1
192.168.15.54
*[main][~/code/tmux-agent]$
</TMUX_HISTORY>

what should I do next?
"""

# result = agent.run_sync(tasks)
# print(result.output["command"])

# result2 = agent.run_sync(output, message_history=result.new_messages())

# print(result2.output["command"])

# with open("messages1.json", "w") as f:
#     json.dump(to_jsonable_python(result2.all_messages()), f, indent=2)

with open("messages1.json", "r") as f:
    messages1 = json.load(f)

messages = ModelMessagesTypeAdapter.validate_python(messages1)

result3 = agent.run_sync(output2, message_history=messages)
print(result3.output["command"])

with open("messages2.json", "w") as f:
    json.dump(to_jsonable_python(result3.all_messages()), f, indent=2)