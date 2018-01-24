from flask import Flask


from MyCapytain.resources.prototypes.cts.inventory import CtsTextInventoryCollection, CtsTextInventoryMetadata
from MyCapytain.resolvers.utils import CollectionDispatcher


from capitains_nautilus.cts.resolver import NautilusCTSResolver
from capitains_nautilus.flask_ext import FlaskNautilus
from flask_nemo.chunker import level_grouper
from flask_nemo import Nemo


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


# Setting up the collections

general_collection = CtsTextInventoryCollection()
poetry = CtsTextInventoryMetadata("poetry_collection", parent=general_collection)
poetry.set_label("Poetry", "eng")
poetry.set_label("Poésie", "fre")

priapeia = CtsTextInventoryMetadata("priapeia_collection", parent=general_collection)
priapeia.set_label("Priapeia", "eng")
priapeia.set_label("Priapées", "fre")

misc = CtsTextInventoryMetadata("id:misc", parent=general_collection)
misc.set_label("Miscellaneous", "eng")
misc.set_label("Textes Divers", "fre")
organizer = CollectionDispatcher(general_collection, default_inventory_name="id:misc")


@organizer.inventory("priapeia_collection")
def organize_my_priapeia(collection, path=None, **kwargs):
    if collection.id.startswith("urn:cts:latinLit:phi1103"):
        return True
    return False


@organizer.inventory("poetry_collection")
def organize_my_poetry(collection, path=None, **kwargs):
    # If we are not dealing with Priapeia
    if not collection.id.startswith("urn:cts:latinLit:phi1103"):
        # Textgroups have a wonderful shortcut to their editions and translations : .readableDescendants
        for text in collection.readableDescendants:
            for citation in text.citation:
                if citation.name == "line":
                    return True
    return False


# Parsing the data
resolver = NautilusCTSResolver(["corpora/additional-texts", "corpora/priapeia"], dispatcher=organizer)
resolver.parse()


flask_app = Flask("Flask Application for Nemo")
nautilus_api = FlaskNautilus(prefix="/api", app=flask_app, resolver=resolver)
nemo = Nemo(
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
