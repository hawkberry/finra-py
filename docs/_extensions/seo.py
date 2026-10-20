from __future__ import annotations

from typing import Any

from sphinx.application import Sphinx

from .llms import write_llms_files
from .metadata import add_metadata


# Connect custom app functions in Docs for SEO
def setup(app: Sphinx) -> dict[str, Any]:
    app.add_config_value("description", "", "html")
    app.add_config_value("project_description", "", "html")
    app.add_config_value("documentation_url", "", "html")
    app.add_config_value("repository_url", "", "html")
    app.add_config_value("changelog_url", "", "html")
    app.add_config_value("issues_url", "", "html")
    app.add_config_value("security_url", "", "html")
    app.add_config_value("adrs_url", "", "html")
    app.add_config_value("consulting_url", "", "html")
    app.add_config_value("support_url", "", "html")
    app.add_config_value("license_url", "", "html")
    app.add_config_value("pypi_url", "", "html")
    app.add_config_value("rss_url", "", "html")
    
    # Connect app functions
    app.connect("html-page-context", add_metadata)
    app.connect("build-finished", write_llms_files)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        }
