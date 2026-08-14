"""Safe, domain-specific research errors."""

from visa_research_agent.domain.models import SourceFailure


class VisaResearchError(RuntimeError):
    """Base error raised when a bounded research run cannot complete safely."""


class FixtureDataError(VisaResearchError):
    """Raised when fixture evidence is missing, inconsistent, or invalid."""


class LiveSourceError(VisaResearchError):
    """Raised when live retrieval cannot produce trustworthy, current official evidence."""


class InsufficientEvidenceError(VisaResearchError):
    """Raised when a plan is refused because load-bearing official evidence is unavailable.

    Carries traveller-safe reasons so the API can explain the refusal instead of failing opaquely.
    """

    def __init__(
        self,
        message: str,
        *,
        reasons: list[str] | None = None,
        failures: list[SourceFailure] | None = None,
    ) -> None:
        super().__init__(message)
        self.reasons = reasons or []
        self.failures = failures or []


class LLMConfigurationError(VisaResearchError):
    """Raised when model extraction is selected without complete safe configuration."""


class LLMExtractionError(VisaResearchError):
    """Raised when model output cannot be produced or validated safely."""
