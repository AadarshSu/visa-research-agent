"""Safe, domain-specific research errors."""


class VisaResearchError(RuntimeError):
    """Base error raised when a bounded research run cannot complete safely."""


class FixtureDataError(VisaResearchError):
    """Raised when fixture evidence is missing, inconsistent, or invalid."""


class LiveSourceError(VisaResearchError):
    """Raised when live retrieval cannot produce trustworthy, current official evidence."""


class LLMConfigurationError(VisaResearchError):
    """Raised when model extraction is selected without complete safe configuration."""


class LLMExtractionError(VisaResearchError):
    """Raised when model output cannot be produced or validated safely."""
