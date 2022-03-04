class General(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NotInitialized(Exception):
    def __init__(self, function: str) -> None:
        super().__init__(f"Not initialized: {function}")


class NotValidQuerry(Exception):
    def __init__(self, obj: str) -> None:
        super().__init__(f"Not valid: {obj}")


class NetworkError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(f"Network error: {msg}") 
