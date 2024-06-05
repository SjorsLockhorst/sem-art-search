class MissingApiKeyError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class ExtractError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg


class EmbeddingError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg
