"""Automatic discovery of official visa sources for a traveller corridor.

Search finds candidates; it never decides what may be believed. Every candidate must sit on a
domain a human already approved, which the existing trust rules in `visa_research_agent.domain`
enforce, so an unofficial page cannot become evidence however highly it ranks.
"""
