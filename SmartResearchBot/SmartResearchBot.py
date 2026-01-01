from google import genai
import requests

def google_search(text):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": text,
        "key": "AIzaSyDrvZfFvqS7KXYdlW66MGSxRmXcDCq8XW0",
        "cx": "20f26929433b348e3",
        "num": 10
    }
    response = requests.get(url, params=params)
    return response.json()
q=input("search something:")
data=google_search(q)
for line in data.get("items"):
    print(line["title"]+'\n')
    print(line["link"]+'\n')
    print(line["snippet"]+'\n')
client = genai.Client(api_key=None)
prompt=input("type what you want to ask:")
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt,
)

print(response.text)
