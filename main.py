import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

response = client.chat.completions.create(
    model="qwen/qwen3-coder:free",  # Free Qwen3 Coder model
    messages=[{"role": "user", "content": "Hello, this is a test!"}]
)

print(response.choices[0].message.content)