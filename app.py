from flask import Flask

from capitains_nautilus.flask_ext import FlaskNautilus
from flask_nemo.chunker import level_grouper

from application.corpus import resolver
from application.extension import MyNemo


def get_citation_scheme(text):
    # We create an empty list to store citations level names
    citation_types = []
    #  We loop over the citation scheme of the Text
    for citation in text.citation:
        # We append the name of the citation level in the list we created
        citation_types.append(citation.name)
    # At this point, we just return
    return citation_types


def generic_chunker(text, getreffs):
    # We build a the citation type
    citation_types = get_citation_scheme(text)
    if "poem" in citation_types:
        level = citation_types.index("poem") + 1
        level_name = "Poem"
        excerpt_length = 1
    else:
        level = len(citation_types)
        level_name = citation_types[-1]
        excerpt_length = 20

    if excerpt_length > 1:
        reffs = level_grouper(text, getreffs, level, excerpt_length)
    else:
        reffs = getreffs(level=level)
        reffs = [(reff, level_name + " " + reff) for reff in reffs]

    return reffs


flask_app = Flask("Flask Application for Nemo")
nautilus_api = FlaskNautilus(name="Nautilus", prefix="/api", app=flask_app, resolver=resolver)
nemo = MyNemo(
    name="InstanceNemo",
    app=flask_app,
    resolver=resolver,
    base_url="",
    css=["assets/css/theme.css"],
    js=["assets/js/empty.js"],
    statics=["assets/images/logo.jpeg"],
    transform={"default": "components/main.xsl"},
    templates={"main": "templates/main"},
    chunker={"default": generic_chunker}
)

if __name__ == "__main__":
    flask_app.run(debug=True)
