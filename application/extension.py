from flask_nemo import Nemo
from flask import Markup, redirect, url_for
from MyCapytain.resources.prototypes.cts.inventory import CtsWorkMetadata, CtsEditionMetadata
from MyCapytain.errors import UnknownCollection
from MyCapytain.common.constants import Mimetypes


class MyNemo(Nemo):
    """ We'll write more there later """
    ROUTES = Nemo.ROUTES + [("/text/<objectId>/full", "r_full_text", ["GET"])]

    def r_full_text(self, objectId, lang=None):
        """ Retrieve the text of the passage
        :param objectId: Collection identifier
        :type objectId: str
        :param lang: Lang in which to express main data
        :type lang: str
        :param subreference: Reference identifier
        :type subreference: str
        :return: Template, collections metadata and Markup object representing the text
        :rtype: {str: Any}
        """
        collection = self.get_collection(objectId)
        if isinstance(collection, CtsWorkMetadata):
            editions = [t for t in collection.children.values() if isinstance(t, CtsEditionMetadata)]
            if len(editions) == 0:
                raise UnknownCollection("This work has no default edition")
            return redirect(url_for(".r_full_text", objectId=str(editions[0].id)))
        text = self.get_passage(objectId=objectId, subreference=None)
        passage = self.transform(text, text.export(Mimetypes.PYTHON.ETREE), objectId)
        return {
            "template": "main::text.html",
            "objectId": objectId,
            "subreference": None,
            "collections": {
                "current": {
                    "label": collection.get_label(lang),
                    "id": collection.id,
                    "model": str(collection.model),
                    "type": str(collection.type),
                    "author": text.get_creator(lang),
                    "title": text.get_title(lang),
                    "description": text.get_description(lang),
                    "citation": collection.citation,
                    "coins": self.make_coins(collection, text, "", lang=lang)
                },
                "parents": self.make_parents(collection, lang=lang)
            },
            "text_passage": Markup(passage),
            "prev": None,
            "next": None
        }
