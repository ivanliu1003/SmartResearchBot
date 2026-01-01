from google import genai

client = genai.Client(api_key=None)
prompt=input("type what you want to ask:")
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt,
)

print(response.text)
