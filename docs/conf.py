# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import json
import sys
import tomllib
from enum import Enum
from importlib import import_module
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from sphinx import addnodes


sys.path.insert(0, str(Path(__file__).parent))


#############################################################################
# -- Config From pyproject.toml ---------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as f:
    config = tomllib.load(f)

project = config["project"]["name"]

version = config["project"]["version"]

author = config["project"]["authors"][0]["name"]

copyright = f"2026, {author}"

description = config["project"]["description"]

project_description = f"{project} - {description}."


# URLS
documentation_url = config["project"]["urls"]["Documentation"]

repository_url = config["project"]["urls"]["Repository"]

issues_url = config["project"]["urls"]["Issues"]

changelog_url = config["project"]["urls"]["Changelog"]

adrs_url = config["project"]["urls"]["ADRs"]

consulting_url = config["project"]["urls"]["Consulting"]

support_url = config["project"]["urls"]["Support"]

license_url = config["tool"]["finra-py"]["license_url"]

pypi_url = config["tool"]["finra-py"]["pypi_url"]


# Metadata
page_descriptions = {
    "index": (
        "finra-py is an open-source Python client library for the FINRA API, "
        "with OAuth 2.0 authentication and HTTPX clients for "
        "Query, Notification and Submission APIs."
        ),
    "getting-started": (
        "Install and configure finra-py, authenticate with the FINRA API "
        "Platform, and make synchronous or asynchronous HTTPX requests from "
        "Python."
        ),
    "auth": (
        "Configure FINRA API authentication with finra-py using OAuth 2.0 "
        "credentials, token management, custom token storage, and "
        "synchronous or asynchronous clients."
        ),
    "client": (
        "Use the finra-py HTTPX client for FINRA API requests with "
        "synchronous and asynchronous clients, session management, enums, "
        "data versioning, and HTTPX responses."
        ),
    "query-api": (
        "Access Equity, Fixed Income, FINRA, Firm, Registration, "
        "and TRACE Report Card datasets using finra-py with filters, "
        "partitions, pagination, and asynchronous requests."
        ),
    "notification-api": (
        "Retrieve FINRA notification event datasets from Python using "
        "the Notification API and finra-py with datetime-range queries and "
        "pagination."
        ),
    "submission-api": (
        "Create, validate, submit, update, and retrieve FINRA regulatory "
        "filings with the Submission API and finra-py, including Form U4, "
        "Form U5, and Form BR."
        ),
    "help": (
        "Troubleshoot finra-py and FINRA API integrations with diagnostic "
        "logging, known API issues, bug-reporting guidance, and solutions."
        ),
    "reference": (
        "Complete API reference for finra-py, covering authentication, "
        "the HTTPX client, Query, Notification and Submission APIs, "
        "utilities, and data types."
        ),
    "adr": (
        "Architecture Decision Records for finra-py including "
        "HTTP response handling, authentication and token management, "
        "and enum representations for FINRA API values."
        ),
    "consulting": (
        "FINRA API consulting for member firms and developers, covering "
        "API integrations, Web EFT migrations, regulatory filing workflows, "
        "and FINRA data systems."
        ),
    }


# LLMs
llms_project_description = (
    "`finra-py` - An unofficial, open-source Python client library for the "
    "FINRA API Platform, providing OAuth 2.0 authentication and "
    "HTTPX-based clients for the Query, Notification, and Submission APIs."
    )

llms_page_descriptions = {
    "index": (
        "Project overview for "
        "`finra-py`, an unofficial, open-source Python client library for the "
        "FINRA API Platform, providing OAuth 2.0 authentication and "
        "HTTPX-based clients for the Query, Notification, and Submission APIs."
        ),
    "getting-started": (
        "Installation and basic usage guide covering client creation, FINRA "
        "API authentication, synchronous and asynchronous HTTPX requests, "
        "response handling, and resource management."
        ),
    "auth": (
        "FINRA API authentication and client-creation guide covering OAuth "
        "2.0 credentials, token management, custom token storage, Mock "
        "datasets, the QA Test Environment API, "
        "and synchronous and asynchronous clients."
        ),
    "client": (
        "HTTPX client documentation covering FINRA API calling conventions, "
        "synchronous and asynchronous clients, session management, enums, "
        "data versioning, request configuration, and standard HTTPX responses."
        ),
    "query-api": (
        "Query API documentation covering Equity, Fixed Income, FINRA, Firm, "
        "Registration, and TRACE Report Card datasets, and API functionality "
        "including fields, filters, sorting, metadata, partitions, "
        "pagination, asynchronous requests, and response formats."
        ),
    "notification-api": (
        "Notification API documentation covering FINRA notification event "
        "datasets and API functionality including datetime-range queries "
        "and pagination."
        ),
    "submission-api": (
        "Submission API documentation covering FINRA regulatory filing "
        "creation, validation, submission, updates, and retrieval, including "
        "Form U4, Form U5, Form BR, Create Individual, and "
        "Non-Registered Fingerprint workflows."
        ),
    "help": (
        "Troubleshooting and support guidance covering diagnostic logging, "
        "bug reports, known FINRA API issues, and common `finra-py` problems."
        ),
    "reference": (
        "Complete Python API reference for `finra-py` covering "
        "authentication, the HTTPX client, Query, Notification and "
        "Submission APIs, utilities, exceptions, and data types."
        ),
    }

llms_project_links_descriptions = {
    "repository": (
        "GitHub source repository, project files, development configuration, "
        "and history."
        ),
    "pypi": (
        "Published `finra-py` package and release information for Python "
        "installation."
        ),
    "issues": (
        "GitHub issue tracker for bug reports and feature requests."
        ),
    "changelog": (
        "Release history and changes between `finra-py` versions."
        ),
    "adr": (
        "Architecture Decision Records for `finra-py` documenting client "
        "architecture and HTTP response handling, authentication and token "
        "management, FINRA API values and enum representations, and "
        "client-side submission validation."
        ),
    "consulting": (
        "Professional FINRA API consulting for member firms and software "
        "teams, covering API integrations, Web EFT migrations, regulatory "
        "filing workflows, and FINRA data systems."
        ),
    "support": (
        "Open-source project support and sponsorship information."
        ),
    "license": (
        "License terms governing use, modification, and distribution of "
        "`finra-py`."
        ),
    }


#############################################################################
# -- General configuration --------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

exclude_patterns = []

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_markdown_builder",
    "_extensions.seo",
    "_extensions.sitemap",
    ]

templates_path = ["_templates"]


#############################################################################
# -- Options for HTML output ------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_css_files = ["custom.css"]

html_extra_path = ["robots.txt"]

html_favicon = "_static/favicon.ico"

html_sidebars = {
    "**": ["sidebar-collapse", "sidebar-nav-bs", "page-toc"],
    }

html_static_path = ["_static"]

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "navigation_depth": 2,
    "navbar_align": "left",
    }

html_title = f"{project} {version}"


#############################################################################
# -- Custom options ---------------------------------------------------------

add_module_names = False

always_use_bars_union = True  # use pipes in docs, not Union[]

autodoc_member_order = "bysource"

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    }

# NOTE: This requires top of file import: from futures import __annotations__
autodoc_type_aliases = {
    "FilingDictType": (
        ":py:type:`FilingDictType <finra.filings.base_filing.FilingDictType>`"
        ),
    "FiltersDictType": (
        ":py:type:`FiltersDictType <finra.filters.FiltersDictType>`"
        ),
    "LabelsMapType": ":py:type:`LabelsMapType <finra.utils.LabelsMapType>`",
    }

markdown_http_base = documentation_url.rstrip("/")

markdown_uri_doc_suffix = ".html"

markdown_flavor = "github"

markdown_anchor_sections = False

markdown_anchor_signatures = False

suppress_warnings = ["toc.not_included"]

toc_object_entries_show_parents = "hide"

viewcode_line_numbers = True

viewcode_follow_imported_members = False


# Skip documentation for certain module level objects
def autodoc_skip_member(app, what, name, obj, skip, options):
    if getattr(obj, "__skip_module_autodoc__", False):
        if what == "module":
            return True
    return skip


#############################################################################
# Hide enum members from left sidebar, but display normally in docs pages

def _resolve_python_object(module_name, object_name):
    """Resolve a Python object by its module and qualified name."""
    try:
        obj = import_module(module_name)
        for part in object_name.split("."):
            obj = getattr(obj, part)
        return obj
    except (AttributeError, ImportError):
        return None


def _is_enum_member(signode):
    """Return True if a Python attribute is an Enum member."""
    module_name = signode.get("module")
    fullname = signode.get("fullname")

    if not module_name or not fullname:
        return False

    try:
        parent_name, member_name = fullname.rsplit(".", 1)
    except ValueError:
        return False

    enum_class = _resolve_python_object(module_name, parent_name)

    return (
        isinstance(enum_class, type)
        and issubclass(enum_class, Enum)
        and member_name in enum_class.__members__
    )


def hide_enum_members_from_toc(app, domain, objtype, contentnode):
    """Exclude Enum members from the Sphinx table of contents."""
    if domain != "py" or objtype != "attribute":
        return

    desc = contentnode.parent

    if desc is None:
        return

    signode = desc.next_node(addnodes.desc_signature)

    if signode is not None and _is_enum_member(signode):
        desc["no-contents-entry"] = True


#############################################################################
# Connect custom function in Docs application setup

def setup(app):
    app.connect("autodoc-skip-member", autodoc_skip_member)
    app.connect("object-description-transform", hide_enum_members_from_toc)

