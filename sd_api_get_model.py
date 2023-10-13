import requests
from pprint import pprint

url = "http://127.0.0.1:7860"

sd_models = requests.get(f"{url}/sdapi/v1/sd-models").json()

sd_models = [i["title"] for i in sd_models]

# pprint(sd_models)

with open("sd_model.txt", '+w', encoding='UTF-8') as f:
    f.write('\n'.join(sd_models))