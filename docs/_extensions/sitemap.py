from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from xml.etree.ElementTree import Element, SubElement, ElementTree, indent

from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder

from . import _metadata
from .urls import canonical_url 


# NOTE: To add a page to sitemap:
#       Create a module in _metadata with the page's name,
#       and import it in _metadata.__init__.


SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

EXCLUDED_PAGES = (
    "genindex",
    "py-modindex",
    "search",
    )

EXCLUDED_PREFIXES = ("_modules/",)

_METADATA_FILES = [m for m in dir(_metadata) if not m.startswith("_")]


def _is_excluded(pagename: str) -> bool:
    if pagename in EXCLUDED_PAGES:
        return True
    
    return any(pagename.startswith(prefix) for prefix in EXCLUDED_PREFIXES)


def _git_timestamp(root: Path, path: Path) -> Optional[datetime]:
    try:
        relative_path = path.relative_to(root)
    except ValueError:
        return None
    
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "log",
                "-1",
                "--format=%cI",
                "--",
                str(relative_path),
                ],
            capture_output=True,
            check=True,
            text=True,
            )
    except (OSError, subprocess.CalledProcessError):
        return None
    
    value = result.stdout.strip()
    if not value:
        return None
    
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError:
        return None
    
    if timestamp.tzinfo is None:
        return None
    
    return timestamp.astimezone(timezone.utc)


def _lastmod(app: Sphinx, pagename: str) -> str:
    root = Path(app.srcdir)
    source = Path(app.env.doc2path(pagename, base=None))
    source_timestamp = _git_timestamp(root, source)
    if source_timestamp is None:
        return datetime.now(timezone.utc).date().isoformat()
    
    update_lastmod_if_changed = [
        root.parent / "pyproject.toml",
        root / "conf.py",
        root / "_extensions" / "metadata.py",
        ]
    if pagename == "":
        update_lastmod_if_changed.append(
            root / "_extensions" / "_metadata" / "index.py"
            )
    elif pagename in _METADATA_FILES:
        _pagename = pagename.replace("-", "_")
        update_lastmod_if_changed.append(
            root / "_extensions" / "_metadata" / f"{_pagename}.py"
            )
    
    timestamps = [source_timestamp]
    for path in update_lastmod_if_changed:
        timestamp = _git_timestamp(root.parent, path)
        if timestamp is not None:
            timestamps.append(timestamp)
    
    return max(timestamps).date().isoformat()


def _priority(pagename: str) -> str:
    if pagename in ("", "index"):
        return "1.0"
    
    return "0.8"


def _changefreq(pagename: str) -> str:
    if pagename in ("", "index"):
        return "weekly"
    
    return "monthly"


def write_sitemap(app: Sphinx, exception: Optional[Exception]) -> None:
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
    
    indent(root, space="  ")
    
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

