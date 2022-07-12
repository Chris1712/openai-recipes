import json
import os
import openai
from pathlib import Path
import re

openai.api_key = os.getenv("OPENAI_API_KEY")

CUISINE_FILE = 'output/cuisines'  # Path to file holding comma separated cuisine list
RECIPE_DICT = 'output/dish_dict.json'  # Path to file holding dict of cuisines -> list of dishes

# Get a completion from the API for a given input, and return a combination of base, prompt, and result
def completion_output(prompt, base):
    base = base + "\n" if base else ""

    result = openai.Completion.create(
        model="text-davinci-002",
        prompt=base + prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    ).choices[0].text.strip()

    return result, base + "\n" + prompt + "\n" + result


def split_list(cs_str):
    return map(lambda s: s.strip(), cs_str.split(", "))


#####################
# CUISINE GENERATION #
#####################

if os.path.exists(CUISINE_FILE):
    # Load existing list
    cuisines = Path(CUISINE_FILE).read_text()
else:
    # Generate list with prompt
    cuisines = completion_output("Give me a long comma-separated list of cuisines.").lower()
    Path(CUISINE_FILE).write_text(cuisines)

##########################
# RECIPE NAME GENERATION #
##########################

if os.path.exists(RECIPE_DICT):
    # Load existing dict
    with open(RECIPE_DICT, 'r') as f:
        dish_dict = json.load(f)
else:
    # Generate dict of cuisine <-> list[recipe] with prompts
    dish_dict = {}
    for cuisine in split_list(cuisines):
        prompt = f"Give me a long comma-separated list of dishes from {cuisine} cuisine."
        dish_list = completion_output(prompt).lower()
        dish_dict[cuisine] = list(split_list(dish_list))
    with open('output/dish_dict.json', 'w', encoding='utf-8') as f:
        json.dump(dish_dict, f, ensure_ascii=False, indent=4)

#############################
# CUISINE CONFIG GENERATION #
#############################
BASE_CONFIG = '''url: ""
baseurl: ""
title: ""
collections_dir: /cuisines
markdown: kramdown

collections:
'''

FULL_CONFIG = BASE_CONFIG + '\n'.join([
  f'''  {cuisine}:
    output: true
    permalink: /:collection/:name
  '''
  for cuisine in dish_dict.keys()
])

Path("generated-recipes/_config.yml").write_text(FULL_CONFIG)
print("Updated generated-recipes/_config.yml")

##########################
# RECIPE POST GENERATION #
##########################
# TODO replace traditional with a list of different styles (quick, vegetarian, healthier)

RECIPE_FORMAT = '''---
layout: recipe
recipe: "{recipe}"
cuisine: "{cuisine}"
description: "{description}"
servings: {servings}
time: {time}
---

## Equipment
{equipment}

## Ingredients
{ingredients}

## Directions
{steps}
'''

def naive_clean(string: str) -> str:
    # In the Jekyll config of a recipe, remove some forbidden characters
    # Add any more replacements in here
    return string.replace(":", " ").strip()

for cuisine, recipe_list in dish_dict.items():
    for recipe in recipe_list:
        recipe_filename = recipe.lower().replace(" ", "-") + ".md"
        directory = f"generated-recipes/cuisines/_{cuisine}"
        filename = f"{directory}/{recipe_filename}"

        # Ensure directory exists for cuisine
        os.makedirs(directory, exist_ok=True)

        if os.path.exists(filename):
            print(f"Already generated {cuisine} - {recipe}")
            continue

        # Perform prompts to generate recipe!
        # Cumulate the base, appending each prompt result onto the previous

        description, base = completion_output(f"What is {cuisine} {recipe}?", None)
        ingredients, base = completion_output(f"A bulleted list of ingredients for traditional {cuisine} {recipe}:", base)
        steps, base       = completion_output("Numbered steps for this recipe:", base)
        equipment, base   = completion_output("Kitchen equipment needed for this recipe:", base)
        servings, base    = completion_output("Number of servings:", base)
        time, base        = completion_output("Time to cook:", base)

        print(servings)
        print(time)

        result_combined = RECIPE_FORMAT.format(
            recipe = recipe,
            cuisine = cuisine,
            description = naive_clean(description),
            servings = naive_clean(servings),
            time = naive_clean(time),
            equipment = equipment,
            ingredients = ingredients,
            steps = steps
        )

        # Update unordered lists to checkbox lists Markdown style
        result = re.sub(
            r"(^-\s?)([A-Za-z0-9])",
            r"- [ ] \2",
            result_combined,
            flags=re.MULTILINE
        )

        # Write formatted recipe to markdown file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result)
            print(f"Wrote {cuisine} - {recipe} to {filename}")
