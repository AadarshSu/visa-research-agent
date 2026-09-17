"""Where the traveller a plan is researched for comes from.

Today there is one source, the request body the form posts. TODO item 55 adds a second, the
traveller's Ofself identity, and this seam exists so that adapter is one new module rather than
edits across the route, extraction and the page. Everything past the route depends on
`TravellerProfile` alone and never learns which source produced it.

The two sources differ in one way worth stating now, because it is easy to copy across by
mistake: **only the anonymous request body may fall back to the default traveller.** A request
naming nobody on the form gets the profile the interface opens on. An Ofself identity lacking a
deciding field must ask the traveller instead, or it would research someone else's corridor for
them without saying so (item 55, rule 4).
"""

from typing import Protocol

from visa_research_agent.api.schemas import VisaPlanRequest
from visa_research_agent.config.traveller import DEFAULT_TRAVELLER_PROFILE
from visa_research_agent.domain.models import TravellerProfile


class TravellerSource(Protocol):
    """Supplies the traveller for one plan request."""

    async def traveller_for(self, request: VisaPlanRequest) -> TravellerProfile: ...


class RequestBodyTravellerSource:
    """The traveller as the request describes it, or the default when it describes nobody."""

    async def traveller_for(self, request: VisaPlanRequest) -> TravellerProfile:
        # The default is what the interface opens on and what the offline Singapore fixture was
        # recorded against.
        if request.traveller is None:
            return DEFAULT_TRAVELLER_PROFILE
        return request.traveller.to_profile()
