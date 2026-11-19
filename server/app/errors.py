class HttpError(Exception):
    """A failure we can show to the caller with a specific HTTP status."""

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
