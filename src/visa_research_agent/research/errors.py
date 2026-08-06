"""Safe, domain-specific research errors."""


class VisaResearchError(RuntimeError):
    """Base error raised when a bounded research run cannot complete safely."""


class FixtureDataError(VisaResearchError):
    """Raised when fixture evidence is missing, inconsistent, or invalid."""
