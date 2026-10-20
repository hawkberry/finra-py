from docutils.nodes import Node
from sphinx.application import Sphinx


page_description = (
    "finra-py is an open-source Python client library for the FINRA API, "
    "with OAuth 2.0 authentication and HTTPX clients for "
    "Query, Notification and Submission APIs."
    )


def _page_title(app: Sphinx, title: Node) -> str:
    return title.astext()


# Include alternate high-resolution favicon as png, preferred by Google
def _metadata_html(app: Sphinx, title: str) -> str:
    favicon_512_png = "/_static/favicon-512.png"
    return f"""
<link rel="icon" href="{favicon_512_png}" sizes="512x512" type="image/png">
""".strip()
