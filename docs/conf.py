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

from sphinx import addnodes


sys.path.insert(0, str(Path(__file__).parent.joinpath("_extensions")))


##############################################################################
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

with open(Path(__file__).parent.parent.joinpath("pyproject.toml"), "rb") as f:
    config = tomllib.load(f)

project = config["project"]["name"]

release = config["project"]["version"]

author = config["project"]["authors"][0]["name"]

copyright = f"2026, {author}"

description = config["project"]["description"]

project_description = f"{project} — {description}."

docs_url = config["project"]["urls"]["Documentation"].rstrip("/") + "/"

repository_url = config["project"]["urls"]["Repository"]

changelog_url = config["project"]["urls"]["Changelog"]

consulting_url = config["project"]["urls"]["Consulting"]

support_url = config["project"]["urls"]["Support"]

issues_url = config["project"]["urls"]["Issues"]

license_url = config["tool"]["finra-py"]["license_url"]

pypi_url = config["tool"]["finra-py"]["pypi_url"]

html_title = f"{project} {release}"

consulting_desc = (
    "Consulting services for FINRA API integration and production systems."
    )

description_llms = (
    "`finra-py` — An Unofficial, Open-Source Python Client Library for the "
    "FINRA API Platform. `finra-py` simplifies integration with FINRA APIs "
    "for accessing public market datasets and regulatory services."
    )

page_descriptions = {
    "index": (
        "finra-py is an unofficial, open-source Python client library for "
        "the FINRA API Platform, providing authentication and access to "
        "FINRA APIs."
        ),
    "getting-started": (
        "Learn how to install and configure finra-py, a Python client for "
        "the FINRA API Platform, and make your first FINRA API request."
        ),
    "auth": (
        "Learn how to authenticate Python applications with the FINRA API "
        "Platform using finra-py and supported FINRA API credentials."
        ),
    "client": (
        "Learn how finra-py provides a Python HTTP client for making "
        "authenticated requests to the FINRA API Platform."
        ),
    "query-api": (
        "Learn how to query FINRA market datasets and regulatory data using "
        "the FINRA Query API and the finra-py Python client."
        ),
    "notification-api": (
        "Learn how to use the FINRA Notification API with finra-py, a Python "
        "client for retrieving FINRA API notifications."
        ),
    "submission-api": (
        "Learn how to use the FINRA Submission API with finra-py, a Python "
        "client for FINRA regulatory data submission workflows."
        ),
    "help": (
        "Find troubleshooting information, known FINRA API issues, "
        "bug-reporting guidance, and support resources for finra-py."
        ),
    "consulting": (
        "FINRA API integration and software development consulting for "
        "production systems using finra-py and the FINRA API Platform."
        ),
    "reference": (
        "Complete finra-py API reference for Python developers, including "
        "the client, API methods, utilities, data types, and FINRA APIs."
        ),
    }


##############################################################################
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx.ext.napoleon",
    "seo",
    ]

templates_path = ["_templates"]

exclude_patterns = []


##############################################################################
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

toc_object_entries_show_parents = "hide"

html_css_files = ["custom.css"]

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


##############################################################################
# -- Custom options ----------------------------------------------------------

autodoc_member_order = "bysource"

add_module_names = False

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    }

always_use_bars_union = True  # use pipes in docs, not Union[]

suppress_warnings = ["toc.not_included"]

viewcode_line_numbers = True

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

# Skip documentation for certain module level objects
def autodoc_skip_member(app, what, name, obj, skip, options):
    if getattr(obj, "__skip_module_autodoc__", False):
        if what == "module":
            return True
    return skip


##############################################################################
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


##############################################################################
# Connect custom function in Docs application setup

def setup(app):
    app.connect("autodoc-skip-member", autodoc_skip_member)
    app.connect("object-description-transform", hide_enum_members_from_toc)

