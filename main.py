import json
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


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


def split_list(list):
    return map(lambda s: s.strip(), list.split(", "))


cuisines = completion_output("Give me a long comma-separated list of cuisines.")
dishes = {}

for cuisine in split_list(cuisines):
    prompt = f"Give me a long comma-separated list of dishes from {cuisine} cuisine."
    dish_list = completion_output(prompt)
    dishes[cuisine] = list(split_list(dish_list))


print(json.dumps(dishes))
