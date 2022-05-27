class ExternalAPIError(Exception):
    """
    Raised for errors related to external api requests.
    """

    def __init__(self, message="ExternalAPIError"):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message
