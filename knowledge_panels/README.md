### How to generate HTML pages for additives from the Yaml page ?

Install the dependencies, then run the command with the list of directories containing the yaml files.

```bash
python3 build_html.py additives ingredients categories nutrients
```

The name of the directory must correspond to a tag type (ex: additives, ingredients, etc).
