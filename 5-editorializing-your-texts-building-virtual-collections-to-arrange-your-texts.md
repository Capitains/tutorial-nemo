Editorializing Your Texts : building virtual collections to arrange your texts
===

We have seen up to now ways to make each individual text look better, either through XSL and styling or through the use of chunkers. The next step will look at how to make browsing of your own collections a little more interesting.

The way Capitains collections are built behind the scene by our resolver is quite simple : it glues all the textgroup it finds into one supermassive collection named "Default Collection". And let's be honnest, that's in no way a good thing to display (I can only imagine a user of the site looking at the menu right, with one link, "default collection". There might be some raised eyebrows).

## So, you said Virtual Collections

Virtual Collections are really simply what they are named : collections that are not covered by your files but are built at run time by Nemo or Nautilus.

Virtual collections are built through the use of MyCapytain TextInventoryCollection's object. In CTS, there is a structure of data which is meant to be TextInventory > Textgroup > Work > Edition or Translation but there was not a Collection of TextInventories. So here you go :

```python
from MyCapytain.resources.prototypes.cts.inventory import CtsTextInventoryCollection, CtsTextInventoryMetadata
```

Once we have imported that, we can build our TextInventories' Collection :

```python
general_collection = CtsTextInventoryCollection()
```

We have three rough kind of texts in our collections :
- Poetry
- Priapeia
- And Miscellaneous

Obviously, we could go deeper but it feels to be good enough. We will then create 3 TextInventories covering these 3 entry points. For each of these TextInventories, we'll :
- create an identifier (it can be fully internal)
- connect it to the general collection we created earlier

```python

poetry = CtsTextInventoryMetadata("urn:perseus:latinLit", parent=general_collection)
poetry.set_label("Poetry", "eng")
poetry.set_label("Poésie", "fre")

priapeia = CtsTextInventoryMetadata("urn:perseus:farsiLit", parent=general_collection)
priapeia.set_label("Priapeia", "eng")
priapeia.set_label("Priapées", "fre")

misc = CtsTextInventoryMetadata("urn:perseus:greekLit", parent=general_collection)
misc.set_label("Miscellaneous", "eng")
misc.set_label("Textes Divers", "fre")
```

Have you seen ? Once we have an inventory, we can actually give it labels in different languages using ISO codes