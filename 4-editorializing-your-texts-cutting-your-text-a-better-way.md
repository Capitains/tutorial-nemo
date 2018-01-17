Editorializing Your Texts : Cutting Your Text a Better Way
===

Nemo is a fit-them-all digital library system that unfortunately is quite stupid when it comes to how to present your text. Because Nemo should fit them all, it makes no assumption on how to present your text and will most likely behave in a way you won't like at all.

**But do not worry : it can be customized easily.**


## Chunkers 

The tools for cutting the text in Nemo are named Chunkers and they provide a simple yet efficient way to present your text in chunks of your choice, either manually or semi-automatically set. Isn't it nice ? 

To understand chunkers, we are gonna need to understand a little how Nemo works. When you set up Nemo, you give it a parser of texts, generally for local readable files such as the one we set up. Nemo does not know much about the text except the metadata it can get : the title, the structure of the text, and any other metadata you threw in. Unfortunately, it happens that it is not much for Nemo to decide. Here is four simple examples based on quite known texts : 

![Medea, the Odyssey, Das Kapital on the Priapeia are on a submarine](images-for-md/citation.systems.png)

Nemo is only aware of that at the beginning. The way Nemo works is then simple : it feeds this information to a chunker that will automatically request available references to build the excerpts presented to the users.

### Default Behaviour

By default, Nemo would be showing those texts by grouping them by 20 at their lowest level. So you would have :

- **For Medea** : Lines 1-20, Lines 21-40, Lines 41-60
- **for the Odyssey**: Book 1 Lines 1-20, Book 1 Lines 21-40, Book 1 Lines 41-60
- **for Das Kapital**: Volume 1 Part 1 Chapter 1 Section 1 Subsections 1-20.
- **for the Priapeia**: Poem 1 lines 1-20, Poem 1 Lines 21-25, Poem 2 lines 1-20, etc.

*Note that the default system would not span over lines if Poem 1 stops at line 25 !*

### Issues

This is great, except that :
- it might cut sentences in half (In fact, the Odyssey sentence on Book 1 line 20 ends at Book 1 line 21)
- It might not be meaningful : Medea is a play, dialogues are meant to be displayed together for the reader to grasp some sense. Scenes and act might be a better-cutting scheme ?
- It might simply fail: Das Kapital does not have subsection everywhere in all chapter. So it might not show all of them...
- It might make the reading heavy : Priapeia are really short poems, it might be more meaningful to show them fully one by one.

## Let's build our own chunker for the Priapeia !

So the Priapeia would be better displayed as poems only. How do we achieve that ? 

### Structure of a Chunker

Well, it's pretty simple. You see, Nemo Chunkers are simple python functions, whose skeleton is something like the following.

```python
def nemo_chunker(text, getreffs):
    """ This is the default chunker which will resolve the reference giving a callback (getreffs) and a text object with its metadata

    :param text: Readable Collection that has a .citation attribute
    :param getreffs: Callback function which retrieves a list of references
    :return: List of passage as tuple such that the first member is a URI version and the second the human one 
                ("1.1-1.20", "Book 1 Line 1-20")
    """
```

The Nemo Chunker is always fed these two parameters. The GetReffs function is a function such that you can :
- run `getreffs(level=1)` and get all reference at the level 1 (For the Priapeia, all poems)
- run `getreffs(level=2)` and get all reference at the level 2 (For the Priapeia, all lines across poems)
- run `getreffs(level=len(text.citation))` and get all reference at the deepest level of citations (For the Priapeia, level 2 : lines)

![Schema of the inner working](images-for-md/chunker.png)

### The simple hard-coded chunker 

Our Priapeia are numbered from 1 to 79 so we could probably do a simple function such as : 

```python
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
```

### Feeding the chunker to Nemo

Great. Should works. To affect a chunker to a specific text, Nemo does the same way that it does for XSL (See *[Playing with the JavaScript, the CSS, the statics and the XSLTs](2-playing-with-js-css-xslt.md)*), using a dictionary :


#### Step 1 - app.py

```python
from flask import Flask
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from capitains_nautilus.flask_ext import FlaskNautilus
from flask_nemo import Nemo


def priapeia_chunker(text, getreffs):
    # We build a list of the number
    poems = []
    for poem_number in range(1, 80):  # Range in Python stops before its end limit
        poems.append(
            (  # Tuple are written with an () in python
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
```

### The larger, automatic chunker

This is a great things but it will be limited once you have a lot of text. This is why it is easy to know a little more about citation system. Readable `Collection`s which are provided as the first parameter of our chunker are :
1. Iterable : you can loop over it
2. Have types : you can know a little about it easily. 

In fact, you could easily retrieve the types looping over it :

```python
def get_citation_scheme(text):
    # We create an empty list to store citations level names
    citation_types = []
    #  We loop over the citation scheme of the Text
    for citation in text.citation:
        # We append the name of the citation level in the list we created
        citation_types.append(citation.name)
    # At this point, we just return
    return citation_types
```

Now, if you'd use it on Priapeia, you'd get `["poem", line"]`. But if it were the Epigrammata of Martial, you'd get `["book", poem", "line"]`. Thing is, these kind of structure often means that the poems are short (unlike `["book", "line"]` that generally indicate epic matter and long poems). So we could probably build a generic poem_chunker that builds onto that. 

We can automatically list poems as we have the ability to use the function `getreffs(level=1)` which will return us parsed reference : for Priapeia, the list would be built by `getreffs(level=1)`, for the Epigrammata  `getreffs(level=2)`. That level can be easily computed in python with the previous information :

```python
citation_types = get_citation_scheme(some_text)
# We check we have some poem
if "poem" in citation_types:
    level = citation_types.index("poem") + 1
```

With this is mind, we could also create a chunker by default. For example, the original default groups by 20 from the lowest level, we might simply want to get to the lowest level every time and see later how to group them :

```python
else:
    level = len(citation_types)
```

And from there, we can build a start for our chunker :

```python
def generic_chunker(text, getreffs):
    # We build a the citation type
    citation_types = get_citation_scheme(text)
    if "poem" in citation_types:
        level = citation_types.index("poem") + 1
    else:
        level = len(citation_types)
```

Now that we have the level, we have to retrieve the references : we'll simply execute the getreffs function on the given level :

```python
    reffs = getreffs(level=level)
```

The getreffs function returns results as a list of string such that getreffs(level=1) of Priapeia would be equal to `["1", "2", ...]`. We can then use those strings to build the readable human version:

```python
    reffs = [(reff, "Priapeia " + reff) for reff in reffs]
```

And complete the others automatically, such that the finale code is :


```python
def generic_chunker(text, getreffs):
    # We build a the citation type
    citations = get_citation_scheme(text)
    if "poem" in citation_types:
        level = citation_types.index("poem") + 1
        level_name = "Priapeia"
    else:
        level = len(citation_types)
        level_name = citation_types[-1]
    reffs = getreffs(level=level)
    reffs = [(reff, level_name + " " + reff) for reff in reffs]

    return reffs
```

And then, the same way XSL has a `default` key in its dictionary, `chunker` has it as well !

#### Step 2 - app.py

```python
from flask import Flask
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from capitains_nautilus.flask_ext import FlaskNautilus
from flask_nemo import Nemo


def get_citation_scheme(text):
    # We create an empty list to store citations level names
    citation_types = []
    #  We loop over the citation scheme of the text
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
    else:
        level = len(citation_types)
        level_name = citation_types[-1]

    reffs = getreffs(level=level)
    reffs = [(reff, level_name + " " + reff) for reff in reffs]

    return reffs


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
    chunker={"default": generic_chunker}
)

if __name__ == "__main__":
    flask_app.run(debug=True)
```

### Reusing original chunker

One last thing before talking about when you should do manual or semi-automatic selection : we really recommend reusing if you do semi-automatic selection the original chunkers from CapiTainS to build your own. 

Let's think about a text built so there is the following citations :

| Book | Line |
| ---- | ---- |
| 1 | 655 |
| 1 | 656 |
| 1 | 657 |
| 1 | … up to … |
| 1 | 674 |
| 1 | 675 |
| 1 | 676 |
| 1 | 677 |
| 1 | … up to … |
| 1 | 684 |
| 1 | 685 |
| 2 | 1 |
| 2 | 2 |
| 2 | 3 |
| 2 | 4 |
| 2 | etc. |

If you'd decide to group lines automatically by 20, you might have a problem where 685 spans then over Book 2 while both are not necessarily following each other in a good reading environment.

The `flask_nemo.chunkers.level_grouper` provide a simple, already coded way to group passages in a clever yet semi-automatic way. For example, it would result in `Book 1 Line 655-675`, `Book 1 Line 675-685` (so only ten lines because there is not enough other lines), `Book 2 Line 1-20`, *etc.* 

The `level_grouper` takes 4 parameters : 
- text (which takes the same text value than your chunker )
- getValidReff (which takes getReff as parameter)
- level : the level at which you want to group your texts
- groupby : the length of the excerpt you want to build

We can from here build the following chunker :

```python
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
```

#### Step 3 - app.py

```python
from flask import Flask
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
    chunker={"default": generic_chunker}
)

if __name__ == "__main__":
    flask_app.run(debug=True)
```

### When should you choose one against the other

We would like to end this tutorial section by a simple note : when you should use a hard-coded chunker over a semi-automatic one.

Hard-coded chunkers (with a specific handcrafted list of passages) are really good if :
1. Your text structure is not gonna change :
	- If you have, say, Book 1 Line 770-790 and then Book 2 Line 1-20 and adds later a 790a, it won't be displayed
2. Your text structure needs a nice editing
	- If things are not as simple as poems sequence such as dialogs, acts and scenes that cross over lines (two competing citations scheme that makes sense together)
3. Your text has uneven depth: this will need some more complicated build from the semi-automatic work. I would recommend crafting it manually if you have this kind of situation (such that you want to show `["Chapter Introduction", "Chapter 1 Part 1", "Chapter 1 Part 2", "Chapter 2", ...]`)

Semi-automatic chunkers are good with :

1. Collection of short forms of texts (Letters, Poems, etc.)
2. Collection of evolving texts
3. Large corpora of automatically transformed texts (although it might be good to move to hard-coded at some point)