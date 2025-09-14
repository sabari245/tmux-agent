from pathlib import Path
import os
import json
from typing import Any, List

from pydantic_core import to_jsonable_python
from pydantic_ai.messages import ModelMessagesTypeAdapter

app = "tmux-agent"
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / app
DATA = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / app
CACHE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / app
CONFIG.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)


class MessageStore:
    def __init__(self, data_dir: Path = DATA):
        self.data_dir = data_dir
        self.chat_history_path = self.data_dir / "chat_history.json"

        if not self.chat_history_path.exists():
            with open(self.chat_history_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def read_chat_history(self) -> List[str]:
        file_path = self.chat_history_path
        if not file_path.exists():
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"read_chat_history: error reading {file_path}: {e}")
            return []
        if isinstance(data, list) and all(isinstance(i, str) for i in data):
            return data
        return []

    def write_chat_history(self, key: str) -> None:
        history = self.read_chat_history()
        try:
            while key in history:
                history.remove(key)
        except ValueError as e:
            print(f"write_chat_history: error removing key {key} from history: {e}")
        history.insert(0, key)
        file_path = self.chat_history_path
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except OSError as e:
            print(f"write_chat_history: error writing {file_path}: {e}")
            return

    def store_pydantic_messages(self, key: str, messages: Any) -> None:
        file_path = self.data_dir / f"{key}.json"
        jsonable = to_jsonable_python(messages)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(jsonable, f, indent=2)
        try:
            self.write_chat_history(key)
        except Exception as e:
            print(f"store_pydantic_messages: error updating history for {key}: {e}")

    def load_pydantic_messages(self, key: str) -> Any:
        file_path = self.data_dir / f"{key}.json"
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        try:
            self.write_chat_history(key)
        except Exception as e:
            print(f"load_pydantic_messages: error updating history for {key}: {e}")
        return ModelMessagesTypeAdapter.validate_python(raw)
