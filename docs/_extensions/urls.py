from sphinx.application import Sphinx


def docs_url(app: Sphinx) -> str:
    return app.config.html_baseurl.rstrip("/") + "/en/latest"


def canonical_url(app: Sphinx, pagename: str) -> str:
    if pagename in ("", "index"):
        return docs_url(app) + "/"
    
    return f"{docs_url(app)}/{pagename}.html"

