"""Host trust rules shared by configuration validation and live retrieval.

Officialness is treated as a property of who controls the domain, never of how a page reads, so
every check here works on hostnames alone.
"""

from collections.abc import Iterable
from urllib.parse import urlsplit

# Labels that appear as the second level of a public suffix. A two-label domain beginning with one
# of these is a suffix such as "gov.sg" or "co.uk" rather than a registrable domain, and trusting
# it would silently trust every site beneath it.
#
# **This list and `bootstrap.GOVERNMENT_NAMESPACE_LABELS` must move together, in one direction:
# every government namespace has to appear here.** They answer different questions — that one asks
# "is this a government namespace?", this one asks "is it too broad to trust whole?" — and a label
# in the first but missing from the second is a hole rather than an omission. Adding `gv` on
# 2026-08-25 found this the hard way: `bmeia.gv.at` reduced to `gv.at`, so trusting Austria's
# ministry would have trusted every Austrian public body under the same namespace, which is what
# refusing `gov.br` whole exists to prevent. `tests/test_trust.py` now asserts the containment
# rather than leaving it to whoever edits one of the two lists.
SUFFIX_MARKER_LABELS = frozenset(
    {
        "ac",
        "co",
        "com",
        "edu",
        "gc",
        "go",
        "gob",
        "gouv",
        "gov",
        "govt",
        "gub",
        "gv",
        "int",
        "mil",
        "net",
        "or",
        "org",
    }
)


def host_of(url: str) -> str:
    """Return the lowercase hostname of a URL, or an empty string when it has none."""

    return (urlsplit(url).hostname or "").lower().rstrip(".")


def is_bare_public_suffix(domain: str) -> bool:
    """True when a domain is too broad to trust, such as "gov.uk" or a single label."""

    labels = domain.lower().strip(".").split(".")
    if len(labels) < 2 or any(not label for label in labels):
        return True
    return len(labels) == 2 and labels[0] in SUFFIX_MARKER_LABELS


def registrable_domain(host: str) -> str:
    """Reduce a hostname to the domain worth trusting.

    Keeps three labels for multi-part public suffixes (`ica.gov.sg`) and two otherwise
    (`example.com`), which matches how `trusted_domains` entries are written by hand.
    """

    labels = host.lower().strip(".").split(".")
    if len(labels) <= 2:
        return ".".join(labels)
    candidate_two = ".".join(labels[-2:])
    # If the last two labels are themselves a suffix, the registrable domain needs a third.
    if is_bare_public_suffix(candidate_two):
        return ".".join(labels[-3:])
    return candidate_two


def host_is_within(host: str, domains: Iterable[str]) -> bool:
    """True when a host equals one of the domains or is a subdomain of one.

    Matching is anchored on a dot boundary, so "london.mfa.gov.sg" is within "mfa.gov.sg" while
    "notmfa.gov.sg" is not.
    """

    normalized_host = host.lower().rstrip(".")
    for domain in domains:
        normalized_domain = domain.lower().strip(".")
        if normalized_host == normalized_domain or normalized_host.endswith(
            f".{normalized_domain}"
        ):
            return True
    return False
