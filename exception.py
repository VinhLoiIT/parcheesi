class InvalidCommandException(Exception):
    def __init__(self, command_str) -> None:
        super().__init__()
        self.command_str = command_str

    def __str__(self) -> str:
        return self.command_str
