from utility_tmux import get_tmux_context, get_tmux_history


def main():
    ctx = get_tmux_context()
    if ctx:
        history = get_tmux_history(ctx)
        if history:
            print("history:", history)
        else:
            print("no history")


if __name__ == "__main__":
    main()
