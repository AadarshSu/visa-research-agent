"""Automatic discovery of official visa sources for a traveller corridor.

Search finds candidates; it never decides what may be believed. A candidate must sit on a domain
belonging to the destination country's own government — governmental *and* under that country's
own top-level domain — which the trust rules in `visa_research_agent.domain` then enforce on every
request, redirect and render. An unofficial page cannot become evidence however highly it ranks.
"""
