class CustomErr(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def print(self) -> None:
        for arg in self.args:
            print(arg)

    def what(self) -> str:
        result = ""
        for arg in self.args:
            result += arg

        return result

class General(CustomErr):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NotInitialized(CustomErr):
    def __init__(self, function: str) -> None:
        super().__init__(f"Not initialized: {function}")


class NotValidQuerry(CustomErr):
    def __init__(self, obj: str) -> None:
        super().__init__(f"Not valid: {obj}")


class NetworkError(CustomErr):
    def __init__(self, msg: str) -> None:
        super().__init__(f"Network error: {msg}") 
