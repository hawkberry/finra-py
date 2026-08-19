from __future__ import annotations

import json
import shutil
from html import escape
from pathlib import Path
from typing import Any, Optional

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder


def _base_url(app: Sphinx) -> str:
    return app.config.docs_url.rstrip("/") + "/en/latest/"


def _canonical_url(app: Sphinx, pagename: str) -> str:
    if pagename in ("", "index"):
        return app.config.docs_url
    
    return f"{_base_url(app)}{pagename}.html"


def _page_title(app: Sphinx, pagename: str) -> str:
    title = app.env.titles.get(pagename)
    if title is not None:
        return title.astext()
    
    return app.config.project


def _page_description(app: Sphinx, pagename: str) -> str:
    return app.config.page_descriptions.get(
        pagename,
        app.config.description,
        )


def _social_image_url(app: Sphinx) -> str:
    return f"{_base_url(app)}_static/social-preview.png"


def _json_ld(app: Sphinx, pagename: str) -> str:
    base_url = _canonical_url(app, "")
    url = _canonical_url(app, pagename)
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
        "version": app.config.release,
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
    url = _canonical_url(app, pagename)
    title = _page_title(app, pagename)
    description = _page_description(app, pagename)
    social_image = _social_image_url(app)
    
    escaped_title = escape(title, quote=True)
    escaped_description = escape(description, quote=True)
    escaped_project_description = escape(
        app.config.project_description, quote=True
        )
    return f"""
<meta name="description" content="{escaped_description}">
<link rel="canonical" href="{url}">

<meta property="og:type" content="website">
<meta property="og:title" content="{escaped_title}">
<meta property="og:description" content="{escaped_description}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{app.config.project}">
<meta property="og:image" content="{social_image}">
<meta property="og:image:alt" content="{escaped_project_description}">
<meta property="og:locale" content="en_US">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escaped_title}">
<meta name="twitter:description" content="{escaped_description}">
<meta name="twitter:image" content="{social_image}">
<meta name="twitter:image:alt" content="{escaped_project_description}">

{_json_ld(app, pagename)}
""".strip()


def add_metadata(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, Any],
    doctree: nodes.document | None,
    ) -> None:
    if not isinstance(app.builder, StandaloneHTMLBuilder):
        return
    
    context.setdefault("metatags", "")
    context["metatags"] += _metadata_html(app, pagename)


def _text_from_doctree(doctree: nodes.document) -> str:
    parts: list[str] = []

    def add(text: str) -> None:
        text = text.strip()
        if text:
            parts.append(text)

    def visit(node: nodes.Node) -> None:
        if isinstance(node, nodes.title):
            add(f"## {node.astext()}")

        elif isinstance(node, nodes.literal_block):
            add(f"```\n{node.astext().strip()}\n```")

        elif isinstance(node, nodes.paragraph):
            add(node.astext())

        elif isinstance(node, nodes.list_item):
            add(f"- {node.astext()}")

        elif isinstance(node, nodes.term):
            add(f"**{node.astext()}**")

        elif isinstance(node, nodes.definition):
            add(node.astext())

        elif isinstance(node, nodes.table):
            rows: list[list[str]] = []

            for row in node.findall(nodes.row):
                cells = [
                    entry.astext().strip()
                    for entry in row.findall(nodes.entry)
                ]
                if cells:
                    rows.append(cells)

            if rows:
                width = max(len(row) for row in rows)

                for row in rows:
                    row.extend([""] * (width - len(row)))

                header = rows[0]
                separator = ["---"] * width

                table = [
                    "| " + " | ".join(header) + " |",
                    "| " + " | ".join(separator) + " |",
                ]

                for row in rows[1:]:
                    table.append("| " + " | ".join(row) + " |")

                add("\n".join(table))

            return

        # Don't recursively visit children of nodes whose complete text
        # we've already extracted.
        if isinstance(node, (
            nodes.title,
            nodes.literal_block,
            nodes.paragraph,
            nodes.list_item,
            nodes.term,
            nodes.definition,
            nodes.table,
        )):
            return

        for child in node.children:
            visit(child)

    for node in doctree.children:
        visit(node)

    return "\n\n".join(parts)


def _write_llms_files(app: Sphinx, exception: Optional[Exception]) -> None:
    if not isinstance(app.builder, StandaloneHTMLBuilder):
        return
    
    if exception is not None:
        return
    
    LLMS_DOCS = (
        "index",
        "getting-started",
        "auth",
        "client",
        "query-api",
        "notification-api",
        "submission-api",
        "help",
        "consulting",
        )
    
    output = Path(app.outdir) # docs-build directory
    python_dir = output.parent # python directory
    
    docs: list[tuple[str, str]] = []
    for docname in LLMS_DOCS:
        if docname not in app.env.found_docs:
            continue
        
        if docname in app.env.metadata:
            metadata = app.env.metadata[docname]
            if metadata.get("orphan"):
                continue
        
        title = app.env.titles.get(docname)
        if title is None:
            continue
        
        docs.append((title.astext(), _canonical_url(app, docname)))
    
    llms = [
        f"# {app.config.project}",
        "",
        f"> {app.config.description_llms}.",
        "",
        "## Project Overview",
        "",
        "- Authentication support for the FINRA API Platform.",
        "- Client interfaces for FINRA API endpoints.",
        "- Support for public market datasets and regulatory APIs.",
        "- Support for Mock datasets and the QA Test Environment API.",
        "- Support for all credential types.",
        "- Support for asynchronous requests (server-side).",
        "- Support for `asyncio` (client-side).",
        "",
        "## Intended Users",
        "",
        "- Software developers integrating with FINRA APIs.",
        "- Financial technology developers.",
        "- Data engineers building financial data applications.",
        "- Researchers using market and regulatory datasets.",
        "- FINRA member firms and organizations.",
        "- Compliance professionals.",
        "",
        "## Installation",
        "",
        "Install from PyPI:",
        "",
        "```bash",
        "python -m pip install finra-py",
        "```",
        "",
        "Import in Python:",
        "",
        "```python",
        "import finra",
        "```",
        "",
        "## Requirements",
        "",
        "- Python >= 3.11.",
        "",
        "## Important Notes",
        "",
        "- `finra-py` is an unofficial client library and is not affiliated "
        "with or endorsed by FINRA.",
        "- Users must obtain appropriate FINRA API credentials.",
        "- Market datasets are available to the public.",
        "- Regulatory datasets require firm or organization credentials.",
        "- API access permissions and data availability are determined by "
        "FINRA.",
        "",
        "## Scope",
        "",
        "`finra-py` provides a Python interface to the FINRA API Platform. It "
        "does not provide financial advice, investment recommendations, "
        "trading strategies, or financial analysis.",
        "",
        "## Documentation",
        "",
        ]
    for title, url in docs:
        llms.append(f"- [{title}]({url})")
    
    llms.extend([
        "",
        "## Project Links",
        "",
        f"- [Repository]({app.config.repository_url}): GitHub Repository.",
        f"- [PyPI]({app.config.pypi_url}): PyPI package.",
        f"- [Changelog]({app.config.changelog_url}): Versioning changes.",
        f"- [Issues]({app.config.issues_url}): Bug reporting and feature "
        "requests.",
        "",
        "## Consulting",
        "",
        f"- [Consulting]({app.config.consulting_url}): "
        f"{app.config.consulting_desc}",
        "",
        "## Support",
        "",
        f"- [Support]({app.config.support_url}): Open source project support "
        "and sponsorship.",
        "",
        "## License",
        "",
        f"- [MIT]({app.config.license_url}): MIT License.",
        "",
        "",
        ])
    
    llms_path = output / "llms.txt"
    llms_path.write_text("\n".join(llms), encoding="utf-8")
    shutil.copy2(llms_path, python_dir / "llms.txt") # copy to python dir
    
    full_parts = [
        f"# {app.config.project}",
        "",
        f"> {app.config.description_llms}.",
        "",
        f"- [Documentation]({app.config.docs_url}): Project documentation.",
        f"- [Repository]({app.config.repository_url}): GitHub Repository.",
        f"- [PyPI]({app.config.pypi_url}): PyPI package.",
        f"- [Changelog]({app.config.changelog_url}): Versioning changes.",
        f"- [Issues]({app.config.issues_url}): Bug reporting and feature "
        "requests.",
        f"- [Consulting]({app.config.consulting_url}): "
        f"{app.config.consulting_desc}",
        f"- [Support]({app.config.support_url}): Open source project support "
        "and sponsorship.",
        f"- [License]({app.config.license_url}): MIT License.",
        "",
        ]
    
    for docname in LLMS_DOCS:
        if docname not in app.env.found_docs:
            continue
        
        doctree = app.env.get_doctree(docname)
        title = app.env.titles.get(docname)
        if title is None:
            continue
        
        full_parts.extend([
            f"# {title.astext()}",
            "",
            f"Source: {_canonical_url(app, docname)}",
            "",
            _text_from_doctree(doctree),
            "",
            "",
            ])
    
    llms_full_path = output / "llms-full.txt"
    llms_full_path.write_text("\n".join(full_parts), encoding="utf-8")
    shutil.copy2(llms_full_path, python_dir / "llms-full.txt") # copy


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_config_value("description", "", "html")
    app.add_config_value("project_description", "", "html")
    app.add_config_value("docs_url", "", "html")
    app.add_config_value("repository_url", "", "html")
    app.add_config_value("changelog_url", "", "html")
    app.add_config_value("consulting_url", "", "html")
    app.add_config_value("support_url", "", "html")
    app.add_config_value("issues_url", "", "html")
    app.add_config_value("license_url", "", "html")
    app.add_config_value("pypi_url", "", "html")
    app.add_config_value("consulting_desc", "", "html")
    app.add_config_value("description_llms", "", "html")
    app.add_config_value("page_descriptions", {}, "html")
    
    app.connect("html-page-context", add_metadata)
    app.connect("build-finished", _write_llms_files)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        }

