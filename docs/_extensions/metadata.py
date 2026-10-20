from __future__ import annotations

import json
from html import escape
from typing import Any, Optional

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder

from . import _metadata
from .urls import canonical_url, docs_url


def _metadata_page(pagename: str) -> str:
    if pagename == "":
        return _metadata.index
    
    return getattr(_metadata, pagename.replace("-", "_"), None)


def _page_title(app: Sphinx, pagename: str) -> str:
    title = app.env.titles.get(pagename)
    if title is None:
        return f"{app.config.project}"
    
    _page = _metadata_page(pagename)
    if _page is not None:
        _metadata_page_title = getattr(_page, "_page_title", None)
        if _metadata_page_title is not None:
            return _metadata_page_title(app, title)
    
    return f"{title.astext()} — {app.config.project}"


def _page_description(app: Sphinx, pagename: str) -> str:
    _page = _metadata_page(pagename)
    if _page is not None:
        return getattr(
            _page, "page_description", app.config.project_description
            )
    
    return app.config.project_description


def _social_image_url(app: Sphinx) -> str:
    return f"{docs_url(app)}/_static/social-preview.png"


def _json_ld(app: Sphinx, pagename: str) -> str:
    base_url = canonical_url(app, "")
    url = canonical_url(app, pagename)
    data = {
        "@context": "https://schema.org",
        "@type": "SoftwareSourceCode",
        "name": app.config.project,
        "description": _page_description(app, pagename),
        "url": base_url,
        "sameAs": [app.config.repository_url, app.config.pypi_url],
        "codeRepository": app.config.repository_url,
        "programmingLanguage": "Python",
        "license": app.config.license_url,
        "version": app.config.version,
        "author": {
            "@type": "Person",
            "name": app.config.author,
            },
        "isPartOf": {
            "@type": "WebSite",
            "name": app.config.project,
            "url": base_url,
            },
        "mainEntityOfPage": url,
        }
    script = json.dumps(data, separators=(",", ":"))
    return f'<script type="application/ld+json">{script}</script>'


def _metadata_html(app: Sphinx, pagename: str) -> str:
    url = canonical_url(app, pagename)
    title = _page_title(app, pagename)
    
    if pagename.startswith("_modules/"): # source code pages
        escaped_description = escape(title, quote=True)
        return f"""
<meta name="description" content="{escaped_description}">
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="{url}">
""".strip()
    
    description = _page_description(app, pagename)
    social_image = _social_image_url(app)
    
    escaped_title = escape(title, quote=True)
    escaped_description = escape(description, quote=True)
    escaped_project_description = escape(
        app.config.project_description, quote=True
        )
    
    metadata = [f"""
<meta name="description" content="{escaped_description}">
<link rel="canonical" href="{url}">
""".strip()]
    
    # Page specific metadata HTML
    _page = _metadata_page(pagename)
    if _page is not None:
        _metadata_page_html = getattr(_page, "_metadata_html", None)
        if _metadata_page_html is not None:
            metadata.append(_metadata_page_html(app, title))
    
    metadata.append(f"""
<meta property="og:type" content="website">
<meta property="og:title" content="{escaped_title}">
<meta property="og:description" content="{escaped_description}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{app.config.project}">
<meta property="og:image" content="{social_image}">
<meta property="og:image:alt" content="{escaped_project_description}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escaped_title}">
<meta name="twitter:description" content="{escaped_description}">
<meta name="twitter:image" content="{social_image}">
<meta name="twitter:image:alt" content="{escaped_project_description}">
{_json_ld(app, pagename)}
""".strip())
    
    return "\n".join(metadata).strip()


# App connect function
def add_metadata(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, Any],
    doctree: Optional[nodes.document]
    ) -> None:
    if not isinstance(app.builder, StandaloneHTMLBuilder):
        return
    
    context.setdefault("metatags", "")
    context["metatags"] += _metadata_html(app, pagename)

