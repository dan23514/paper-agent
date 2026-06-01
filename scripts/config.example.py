"""Shared configuration for paper-agent scripts.

Copy this file to `config.py` and set MAILTO_EMAIL to your own email address.
`config.py` is gitignored so your email is never committed.
"""

# Set your email for OpenAlex / CrossRef polite pool (higher rate limits, no key required)
MAILTO_EMAIL = "your-email@example.com"

OPENALEX_BASE = "https://api.openalex.org"
CROSSREF_BASE = "https://api.crossref.org"

# Default SJR data year (falls back to earlier years if CSV not found)
SJR_YEAR = 2025
