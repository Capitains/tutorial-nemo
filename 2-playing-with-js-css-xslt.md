Playing with the JavaScript, the CSS, the statics and the XSLTs
===

You can add or overwrite the Nemo default CSS and Javascript files. There is many way to do so, but the simplest is
most probably to do so at the set-up of the Nemo object.

## Adding CSS or Javascripts

I am not a super huge fan of the capitalization Nemo adds by default to the menu on the left. For this reason, I have
created the file `theme.css` at the path `/assets/css/theme.css`.

#### `assets/css/theme.css`

```css
ul.menu li a {
    text-transform: none;
    font-style: italic;
    font-variant: normal;
}
```

I can now adds this file to the Nemo instance by declaring it at the instantiation :

```python
nemo = Nemo(
    name="InstanceNemo",
    app=flask_app,
    resolver=resolver,
    base_url="",
    css=["assets/css/theme.css"]
)
```

**Warning**: a limitation in Nemo (1.0.1) requires you to put your css into subfolder of your current app (it would not have
worked if `theme.css` was in the same folder as `app.py`.
You can track this issue [here](https://github.com/Capitains/flask-capitains-nemo/issues/108)

#### Step 1 - app.py

```python
from flask import Flask
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from capitains_nautilus.flask_ext import FlaskNautilus
from flask_nemo import Nemo


flask_app = Flask("Flask Application for Nemo")
resolver = NautilusCTSResolver(["corpora/additional-texts", "corpora/priapeia"])
resolver.parse()

nautilus_api = FlaskNautilus(prefix="/api", app=flask_app, resolver=resolver)
nemo = Nemo(
    name="InstanceNemo",
    app=flask_app,
    resolver=resolver,
    base_url="",
    css=["assets/css/theme.css"]
)

if __name__ == "__main__":
    flask_app.run(debug=True)
```

### Adding Javascript and static (eg. images)

Javascript and static images works the same way : you set up the parameters of `Nemo()` instantiation using `js=` and `statics=` : 

```python
nemo = Nemo(
    name="InstanceNemo",
    app=flask_app,
    resolver=resolver,
    base_url="",
    css=["assets/css/theme.css"],
    js=["assets/js/empty.js"],
    statics=["assets/images/logo.jpeg"]
)
```

The CSS and JS files are automatically added to every pages. However, for the static, is is possible to call them from your JS or CSS files using the result of the *Flask* function `url_for(".secondary_assets", filetype="js", asset="empty.js")` where filetype can either be `js`, `css` or `static`. This will result in URIs such as `/assets/nemo.secondary/css/theme.css`,  `/assets/nemo.secondary/js/empty.js` and  `/assets/nemo.secondary/static/logo.jpg`.

**Version 1.0.1:** Note that the folder path is not taken into account : path are limited to the file name. *[See the issue for this](https://github.com/Capitains/flask-capitains-nemo/issues/110)*


#### Step 2 - app.py

```python
from flask import Flask
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from capitains_nautilus.flask_ext import FlaskNautilus
from flask_nemo import Nemo


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
    statics=["assets/images/logo.jpeg"]
)

if __name__ == "__main__":
    flask_app.run(debug=True)
```

## Replace entirely the static folders of Nemo

**Important**: Note that doing so might result in **missing file** if you do not replace all files by file having the same name. You might want to edit templates to avoid calling removed statics. See the chapter about changing templates

You can replace the default statics used by Nemo by changing the static folder of Nemo. To do so, you need to create a static folder and link to it at the instantiation of the object. For example, if we wanted to overwrite them by using our newly created `assets` folder, we would do :

```python
nemo = Nemo(
    name="InstanceNemo",
    app=flask_app,
    resolver=resolver,
    base_url="",
    static_folder="./assets/"
)
```

This would result in overwriting the complete set of current file. If you are doing that without updating the original templates, we heavily recommend to copy the folders in the [`flask_nemo/data/static`](https://github.com/Capitains/flask-capitains-nemo/tree/master/flask_nemo/data/static) folder of the original repository to make sure you are not forgetting any CSS, Javascripts or Images.


#### Step 3 - app.py

This script will run with a readable UI only if you have an equivalent file for every file originally in `flask_nemo/data/static`.

```python
from flask import Flask
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from capitains_nautilus.flask_ext import FlaskNautilus
from flask_nemo import Nemo


flask_app = Flask("Flask Application for Nemo")
resolver = NautilusCTSResolver(["corpora/additional-texts", "corpora/priapeia"])
resolver.parse()

nautilus_api = FlaskNautilus(prefix="/api", app=flask_app, resolver=resolver)
nemo = Nemo(
    name="InstanceNemo",
    app=flask_app,
    resolver=resolver,
    base_url="",
    static_folder="./assets/"
)

if __name__ == "__main__":
    flask_app.run(debug=True)
```

## Playing with XSLT and XML Transformation

If you are not using any Javascript for transforming your TEI XML (such as *[CETEIcean](https://github.com/TEIC/CETEIcean)*) or using plain CSS to match your TEI nodes, you might want to use either XSLT or Python transformation. And there is nothing easier than that with Nemo.

We have copied an XSI from the [CTS Leipzig UI](https://raw.githubusercontent.com/OpenGreekAndLatin/cts_leipzig_ui/master/cts_leipzig_ui/data/assets/static/xslt/edition.xsl) into `components/main.xsl` in the current directory. This XSL is meant for [TEI Epidoc editions, translations or commentary](http://www.stoa.org/epidoc/gl/latest/).

Now that we have an XSLT, we can simply add it to Nemo. Nemo takes a parameter `transform=` at instantiation which needs to be a dictionary where keys behave such as
- the key `default` represents the default behaviour for transformation
- any other key should be an identifier for a specific text, in case you have a transformation routine specific to each of your text or one single text in all your texts

and value behaves such as :
- as string, they represent the path to an XSLT of your choice. Nemo will makes the parsing itself and will run it automatically. For us, this means we'll use `/components/main.xsl` as the value
- [*Advanced Users only*] as *Callable* (function or object), they will transform the XML objet itself. The callable is passed four parameters in the following order: a [Collection object](http://mycapytain.readthedocs.io/en/2.0.6/MyCapytain.classes.html#collection), a [lxml.etree.Element object](http://lxml.de/tutorial.html#the-element-class), the identifier of the current object as string, the identifier of the subreference as a string.

In our case, the result of the instantiation will be 

```python
nemo = Nemo(
    # ...
    transform={"default": "components/main.xsl"}
)
```

#### Step 4 - app.py

This script will run with a readable UI only if you have an equivalent file for every file originally in `flask_nemo/data/static`.

```python
from flask import Flask
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from capitains_nautilus.flask_ext import FlaskNautilus
from flask_nemo import Nemo


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
    transform={"default": "components/main.xsl"}
)

if __name__ == "__main__":
    flask_app.run(debug=True)

```

## Next

Unhappy with the templates ? [Let's go modify them](3-modifying-the-templates.md)