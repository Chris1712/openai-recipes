from google_images_search import GoogleImagesSearch
import os
import json

# set environment variables: GCS_DEVELOPER_KEY, GCS_CX
api_key = os.getenv("GCS_DEVELOPER_KEY")
custom_search_id = os.getenv("GCS_CX")
gis = GoogleImagesSearch(api_key, custom_search_id)
print(f"Using API Key {api_key} and Search ID {custom_search_id}")

def search_params(cuisine: str, recipe: str) -> dict:
    return  {
        'q': f'{cuisine} {recipe} recipe',
        'num': 1,
        'fileType': 'jpg',
    }

# load existing recipes
with open("output/dish_dict.json", 'r') as f:
    dish_dict = json.load(f)

for cuisine, recipe_list in dish_dict.items():
    if cuisine not in ["cambodian", "chinese", "indian", "japanese", "korean", "thai", "vietnamese"]:
        continue

    for recipe in recipe_list:
        file_name = recipe.lower().replace(" ", "-")
        directory_path = f'generated-recipes/assets/photos/{cuisine}/'
        if os.path.exists(directory_path + file_name + ".jpg"):
            print(f"{cuisine} {recipe} image already retrieved")
            continue

        params = search_params(cuisine, recipe)
        print(f"Performing search: {params}")

        gis.search(
            search_params=params,
            path_to_dir=directory_path,
            custom_image_name=file_name
        )
