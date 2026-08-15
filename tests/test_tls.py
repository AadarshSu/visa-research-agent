"""Completing certificate chains without weakening verification."""

import ssl

from visa_research_agent.research.tls import build_ssl_context, load_extra_intermediates


def test_verification_and_hostname_checking_stay_on() -> None:
    """The whole point: chains are completed, nothing is trusted blindly.

    If these ever loosen, anyone able to intercept the connection could impersonate an immigration
    authority and dictate what documents a traveller is told to bring.
    """

    context = build_ssl_context()

    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True


def test_the_bundled_intermediates_are_loaded() -> None:
    pems = load_extra_intermediates()

    assert pems, "at least one intermediate should be bundled"
    for pem in pems:
        assert "BEGIN CERTIFICATE" in pem


def test_the_intermediate_that_vietnams_evisa_portal_omits_is_present() -> None:
    """Vietnam's official e-visa portal serves a genuine GlobalSign certificate but omits the
    intermediate linking it to the root, so the connection fails without this."""

    names: set[str] = set()
    for certificate in build_ssl_context().get_ca_certs():
        for field in certificate.get("subject", ()):
            for pair in field:
                if len(pair) == 2:
                    names.add(pair[1])

    assert "GlobalSign RSA OV SSL CA 2018" in names


def test_the_standard_trust_store_is_still_the_base() -> None:
    """Adding intermediates must extend the default trust store, never replace it."""

    certificates = build_ssl_context().get_ca_certs()

    # A handful of bundled intermediates plus the full public root store.
    assert len(certificates) > 50
