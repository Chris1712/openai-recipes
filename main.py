import json
import os
import openai
from pathlib import Path

openai.api_key = os.getenv("OPENAI_API_KEY")

CUISINE_FILE = 'output/cuisines'  # Path to file holding comma separated cuisine list
RECIPE_DICT = 'output/dish_dict.json'  # Path to file holding dict of cuisines -> list of dishes

# Get a completion from the API for a given input, and print it
def completion_output(text):
    result = openai.Completion.create(
        model="text-davinci-002",
        prompt=text,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    ).choices[0].text.strip()
    print(text)
    print(result)
    print("-"*50)
    return result


def split_list(cs_str):
    return map(lambda s: s.strip(), cs_str.split(", "))


# First generate (or load) list of cuisines (like 'italian, indian, persian' etc.)
if os.path.exists(CUISINE_FILE):
    print("Loading existing cuisine list")
    cuisines = Path(CUISINE_FILE).read_text()
else:
    cuisines = completion_output("Give me a long comma-separated list of cuisines.")
    Path(CUISINE_FILE).write_text(cuisines)


# Then generate (or load) dict of cuisine name -> list of recipe names
if os.path.exists(RECIPE_DICT):
    print("Loading existing recipe dict")
    with open(RECIPE_DICT, 'r') as f:
        dish_dict = json.load(f)
else:
    dish_dict = {}
    for cuisine in split_list(cuisines):
        prompt = f"Give me a long comma-separated list of dishes from {cuisine} cuisine."
        dish_list = completion_output(prompt)
        dish_dict[cuisine] = list(split_list(dish_list))
    with open('output/dish_dict.json', 'w', encoding='utf-8') as f:
        json.dump(dish_dict, f, ensure_ascii=False, indent=4)

# Make directories for each cuisine:
for cuisine in dish_dict.keys():
    Path(f"output/recipes/{cuisine.lower()}").mkdir(parents=True, exist_ok=True)

# Finally generate and write an actual recipe for each
# Todo replace traditional with a list of different styles (quick, vegetarian, healthier)
for cuisine, recipeList in dish_dict.items():
    for recipe_name in recipeList:
        ingredients_prompt = f"A bulleted list of ingredients for traditional {cuisine} {recipe_name}:"
        ingredients_result = completion_output(ingredients_prompt)
        steps_prompt = ingredients_prompt + '\n' + ingredients_result + '\nNumbered steps for this recipe:'
        steps_result = completion_output(steps_prompt)
        tools_prompt = steps_prompt + '\n' + steps_result + '\nKitchen equipment needed for this recipe:'
        tools_result = completion_output(tools_prompt)

        filenameStart = f"output/recipes/{cuisine}/{recipe_name}".lower()
        with open(f"{filenameStart}-ingredients.txt", 'w', encoding='utf-8') as f:
            f.write(ingredients_result)
        with open(f"{filenameStart}-steps.txt", 'w', encoding='utf-8') as f:
            f.write(steps_result)
        with open(f"{filenameStart}-tools.txt", 'w', encoding='utf-8') as f:
            f.write(tools_result)
