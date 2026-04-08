from typing import Protocol

class UserInterface(Protocol):
    def error(self, msg: str) -> None:
        pass


class ConsoleUI(UserInterface):
    def error(self, msg: str) -> None:
        print(msg)
