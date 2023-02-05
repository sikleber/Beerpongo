def append_action_to_state(state: str, action: str) -> str:
    if len(state) == 0:
        return action
    else:
        return state + "," + action
