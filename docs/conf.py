# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


##############################################################################
#-- Get configuration from pyproject.toml ------------------------------------

import configparser
import json
import re
from pathlib import Path


def quote_dict_keys(s):
    s = s.strip()
    s = re.sub(r'([{\[,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*=\s*)', r'\1"\2"\3', s)
    s = s.replace('=', ':').replace(',]', ']')
    try:
        return json.loads(s)
    except json.decoder.JSONDecodeError:
        return s


def remove_quotes(value):
    if isinstance(value, str):
        value = quote_dict_keys(value.replace('\n', ''))
        
    if isinstance(value, dict):
        for k, v in value.items():
            value[k] = remove_quotes(v)
        return value
    
    if isinstance(value, list):
        return list(map(remove_quotes, value))
    
    if isinstance(value, str):
        if value.startswith(('"', "'")):
            value = value[1:]
        if value.endswith(('"', "'")):
            value = value[:-1]
    return value


def get_pyproject_config():
    config = configparser.ConfigParser()
    config.read(Path(__file__).parent.parent.joinpath("pyproject.toml"))
    config = json.dumps(config._sections)
    config = json.loads(config)
    return remove_quotes(config)


config = get_pyproject_config()


##############################################################################
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = config["project"]["name"]

release = config["project"]["version"]

author = config["project"]["authors"][0]["name"]

copyright = f"2026, {author}"

html_title = f"{project.split('.')[0]} {release}"


##############################################################################
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx.ext.napoleon",
    ]

templates_path = ["_templates"]

exclude_patterns = []


##############################################################################
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

toc_object_entries_show_parents = "hide"

html_baseurl = "https://finra.hawkberry.com/en/latest/"

html_context = {
    "description": (
        "Official documentation for finra-py, an unofficial, open-source "
        "Python client library for the FINRA API Platform."
        )
    }

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

from enum import Enum
from importlib import import_module

from sphinx import addnodes


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

