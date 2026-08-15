"""Completing certificate chains that authorities fail to send.

Some government servers present only their own certificate and omit the intermediate linking it to
a trusted root. Browsers fetch that missing link automatically; Python does not, so the connection
fails even though the certificate is genuine. Vietnam's official e-visa portal is one such site.

The fix is to supply the missing intermediates, **never** to disable verification. Certificate
checking stays fully on, so a site that cannot prove who it is still cannot be read — which matters
more here than almost anywhere, because an attacker able to impersonate an immigration authority
could dictate what documents a traveller is told to bring.

Every certificate loaded here must already chain to a root in the standard trust store, so nothing
new becomes trusted; only a server's misconfiguration is worked around.
"""

import ssl
from functools import lru_cache
from importlib.resources import files

import certifi

INTERMEDIATES_PACKAGE = "visa_research_agent.config.tls_intermediates"


def load_extra_intermediates() -> list[str]:
    """The PEM text of every bundled intermediate certificate."""

    directory = files(INTERMEDIATES_PACKAGE)
    return [
        entry.read_text(encoding="ascii")
        for entry in sorted(directory.iterdir(), key=lambda item: item.name)
        if entry.name.endswith(".pem")
    ]


@lru_cache(maxsize=1)
def build_ssl_context() -> ssl.SSLContext:
    """A verifying TLS context: the standard trust store plus the missing intermediates.

    `create_default_context` keeps hostname checking and certificate verification enabled. The
    extra certificates only complete chains; they cannot make an untrusted certificate valid,
    because each is itself signed by a root already in the store.
    """

    context = ssl.create_default_context(cafile=certifi.where())
    for pem in load_extra_intermediates():
        context.load_verify_locations(cadata=pem)
    return context
