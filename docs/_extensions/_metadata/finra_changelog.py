from html import escape

from sphinx.application import Sphinx


page_description = (
    "Unofficial changelog for the FINRA API and related documentation, "
    "tracking dataset, documentation, and API changes by kind, section_type, "
    "and priority."
    )


# Include link to RSS feed
def _metadata_html(app: Sphinx, title: str) -> str:
    rss = app.config.rss_url
    rss_title = f"{title} &#8212; RSS Feed"
    _title = escape(rss_title, quote=True)
    return f"""
<link rel="alternate" type="application/rss+xml" title="{_title}" href="{rss}">
""".strip()
