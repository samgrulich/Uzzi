class NotInitialized(Exception):
    def __init__(self, function: str) -> None:
        super().__init__(f"{function} not initialized")


class NetworkError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(f"Network error: {msg}") 
