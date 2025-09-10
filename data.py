from pathlib import Path
import os
import json
from typing import Any, List

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

    def store_message(self, key: str, messages: List[Any]) -> None:
        """
        Store the list of messages in a JSON file named after the key in the DATA folder.
        """
        file_path = self.data_dir / f"{key}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2)

    def load_message(self, key: str) -> List[Any]:
        """
        Load and return the list of messages from the JSON file named after the key in the DATA folder.
        Returns an empty list if the file does not exist.
        """
        file_path = self.data_dir / f"{key}.json"
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            messages = json.load(f)
        return messages
