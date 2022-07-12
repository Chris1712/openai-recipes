## Initial setup

Obtain openapi key from [openai.com](https://beta.openai.com/account/api-keys)

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY='ABC-123'
```

## Installing stuff

```
pip install whatever
pip freeze > requirements.txt
```

## Jekyll Local development

```sh
jekyll serve --livereload
```

# Recipe Generation Config
`main.py` holds two relevant templates:
- `BASE_CONFIG` that describes jekylls config, including the list of cuisines that will appear on the homepage.
- `RECIPE_FORMAT` that describes the jekyll template for the recipe.
