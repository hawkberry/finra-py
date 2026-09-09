from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder

from .urls import canonical_url, docs_url 


SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

EXCLUDED_PAGES = {
    "genindex",
    "py-modindex",
    "search",
    }

EXCLUDED_PREFIXES = ("_modules/",)


def _is_excluded(pagename: str) -> bool:
    if pagename in EXCLUDED_PAGES:
        return True
    
    return any(pagename.startswith(prefix) for prefix in EXCLUDED_PREFIXES)


def _lastmod(app: Sphinx, pagename: str) -> str:
    build_time = datetime.now(timezone.utc)
    source = Path(app.env.doc2path(pagename, base=None))
    if source.exists():
        source_time = datetime.fromtimestamp(
            source.stat().st_mtime,
            timezone.utc
            )
        build_time = max(build_time, source_time)

    return build_time.date().isoformat()


def _priority(pagename: str) -> str:
    if pagename in ("", "index"):
        return "1.0"

    return "0.8"


def _changefreq(pagename: str) -> str:
    if pagename in ("", "index"):
        return "weekly"

    return "monthly"


def write_sitemap(app: Sphinx, exception: Exception | None) -> None:
    if exception is not None:
        return
    
    if not isinstance(app.builder, StandaloneHTMLBuilder):
        return
    
    root = Element("urlset", {"xmlns": SITEMAP_NS})
    for pagename in sorted(
        app.env.found_docs,
        key=lambda pagename: (pagename not in ("", "index"), pagename)
        ):
        if _is_excluded(pagename):
            continue
        
        url = SubElement(root, "url")
        SubElement(url, "loc").text = canonical_url(app, pagename)
        SubElement(url, "lastmod").text = _lastmod(app, pagename)
        SubElement(url, "changefreq").text = _changefreq(pagename)
        SubElement(url, "priority").text = _priority(pagename)
    
    output = Path(app.outdir) / "sitemap.xml"
    ElementTree(root).write(
        output,
        encoding="UTF-8",
        xml_declaration=True
        )


#############################################################################
# Connect custom function in Docs application setup

def setup(app: Sphinx) -> dict:
    app.connect("build-finished", write_sitemap)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        }

