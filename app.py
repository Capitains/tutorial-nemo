from flask import Flask
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from capitains_nautilus.flask_ext import FlaskNautilus
from flask_nemo import Nemo


def priapeia_chunker(text, getreffs):
    # We build a list of the number
    poems = []
    for poem_number in range(1, 80):  # Range in Python stops before its end limit
        poems.append(
            (  # Tuple are written with a () in python
                str(poem_number),                   # First the reference for the URI as string
                "Priapeia "+ str(poem_number)  # Then the readable format for humans
            )
        )
    return poems


flask_app = Flask("Flask Application for Nemo")
resolver = NautilusCTSResolver(["corpora/additional-texts", "corpora/priapeia"])
resolver.parse()

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
    chunker={"urn:cts:latinLit:phi1103.phi001.lascivaroma-lat1": priapeia_chunker}
)

if __name__ == "__main__":
    flask_app.run(debug=True)
