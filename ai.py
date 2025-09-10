from utility_tmux import get_tmux_context, get_tmux_history, send_keys_to_pane


def main():
    ctx = get_tmux_context()
    if ctx:
        history = get_tmux_history(ctx)
        if history:
            print("history:", history)
        else:
            print("no history")

        send_keys_to_pane(ctx, "echo 'hello'", suppress_history=True)


if __name__ == "__main__":
    main()
