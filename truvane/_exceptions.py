class TruvaneError(Exception):
    """Base class for all Truvane SDK errors."""


class TruvaneAuthError(TruvaneError):
    """Missing, invalid, or revoked API key (HTTP 401)."""


class TruvaneRateLimitError(TruvaneError):
    """Rate limit or monthly quota exceeded (HTTP 429)."""


class TruvaneValidationError(TruvaneError):
    """Bad request — invalid image, unsupported format, too large, or a
    rejected image_url (HTTP 413/422)."""


class TruvaneAPIError(TruvaneError):
    """Unexpected error response from the API."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code
