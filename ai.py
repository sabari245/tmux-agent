import sys
import platform
from typing import Any, Dict

import pyperclip

from utility import get_tmux_context, get_tmux_history
from agent import generate_command


def _get_system_info() -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "platform": platform.platform(aliased=True, terse=False),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
    }
    # Attempt to get memory info from /proc/meminfo on Linux
    try:
        if platform.system().lower() == "linux":
            meminfo: Dict[str, str] = {}
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val = parts[1].strip()
                        meminfo[key] = val
            info["mem_total"] = meminfo.get("MemTotal")
            info["mem_free"] = meminfo.get("MemFree")
    except Exception:
        pass
    return info


def _last_n_lines(text: str, n: int) -> str:
    lines = text.splitlines() if text else []
    return "\n".join(lines[-n:]) if lines else ""


def main() -> None:
    if len(sys.argv) != 2:
        print('usage: ai.py "your prompt here"')
        return

    prompt = sys.argv[1]
    ctx = get_tmux_context()
    if not ctx:
        print("This terminal is not yet supported. Please use tmux for now.")
        return

    history_full = get_tmux_history(ctx) or ""
    history = _last_n_lines(history_full, 1000)
    system_info = _get_system_info()

    command = generate_command(prompt, history, system_info)
    pyperclip.copy(command)
    print(f"Copied to clipboard: {command}")


if __name__ == "__main__":
    import os

    main()
