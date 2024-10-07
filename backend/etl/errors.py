class ExtractError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg


class EmbeddingError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg
