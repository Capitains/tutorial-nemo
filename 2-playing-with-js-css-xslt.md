Playing with the JavaScript, the CSS and the XSLTs
===

You can add or overwrite the Nemo default CSS and Javascript files. There is many way to do so, but the simplest is
most probably to do so at the set-up of the Nemo object.

## Adding CSS or Javascripts

I am not a super huge fan of the capitalization Nemo adds by default to the menu on the left. For this reason, I have
created the file `theme.css` at the path `/assets/css/theme.css`.

### `assets/css/theme.css`

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

**Warning**: a bug in Nemo (1.0.1) requires you to put your css into subfolder of your current app (it would not have
worked if `theme.css` was in the same folder as `app.py`.
You can track this issue [here](https://github.com/Capitains/flask-capitains-nemo/issues/108)

### Step 1 - app.py

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