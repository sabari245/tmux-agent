import os
import subprocess
import libtmux
from typing import TypedDict


class TmuxContext(TypedDict):
    session: libtmux.Session
    window: libtmux.Window
    pane: libtmux.Pane


def get_tmux_context() -> TmuxContext | None:
    """
    Return a dict with libtmux objects {"session", "window", "pane"} when
    running inside tmux. Returns None if any of the required values cannot be
    resolved.
    """
    tmux_env = os.environ.get("TMUX")
    if not tmux_env:
        return None

    # Determine session name
    try:
        session_name = subprocess.check_output(
            ["tmux", "display-message", "-p", "#S"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        parts = tmux_env.split(",")
        session_name = parts[1] if len(parts) >= 2 else None
    if not session_name:
        return None

    server = libtmux.Server()
    try:
        session = server.sessions.get(session_name=session_name)
    except Exception:
        return None
    if not session:
        return None

    # Window: use active_window (replacement for deprecated attached_window)
    try:
        # active_window may be a property or callable depending on libtmux version
        window = session.active_window if hasattr(session, "active_window") else None
        if callable(window):
            window = window()
    except Exception:
        return None
    if not window:
        return None

    # Pane: resolve current pane id via tmux and find in window.panes
    try:
        pane_id = subprocess.check_output(
            ["tmux", "display-message", "-p", "#{pane_id}"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return None

    # Prefer window.active_pane when available
    try:
        active_pane = window.active_pane if hasattr(window, "active_pane") else None
        if callable(active_pane):
            active_pane = active_pane()
        if getattr(active_pane, "pane_id", None) == pane_id:
            pane = active_pane
        else:
            pane = None
            for p in window.panes:
                if getattr(p, "pane_id", None) == pane_id:
                    pane = p
                    break
    except Exception:
        pane = None

    if not pane:
        return None

    return {"session": session, "window": window, "pane": pane}


def get_tmux_history(context: TmuxContext | None) -> str | None:
    """
    Return the full content history of the pane from the provided `TmuxContext`.

    Returns a list of lines (most recent last) or None if the history cannot be
    retrieved (for example, when not running inside tmux or the pane is missing).
    """
    if not context:
        return None

    pane = context.get("pane")
    if not pane:
        return None

    pane_id = getattr(pane, "pane_id", None)
    if not pane_id:
        return None

    try:
        # Capture the entire pane history from the start (-S -) and print (-p)
        output = subprocess.check_output(
            ["tmux", "capture-pane", "-p", "-S", "-", "-t", str(pane_id)],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return output.strip()
    except Exception:
        # Fall back to asking the libtmux Pane object if it provides a helper
        try:
            if hasattr(pane, "capture_pane"):
                captured = pane.capture_pane()
                # capture_pane may return a string or list depending on version
                if isinstance(captured, str):
                    return captured.strip()
                if isinstance(captured, (list, tuple)):
                    return "\n".join(line.strip() for line in captured).strip()
        except Exception:
            pass

    return None
