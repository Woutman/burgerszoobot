import os

from dotenv import load_dotenv
import openai


load_dotenv("api_keys.env")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def query_gpt(chat_history: list[dict[str, str]]) -> str:
    response = client.chat.completions.create(
        messages=chat_history, 
        model="gpt-4o-2024-08-06",
        temperature=0.7,
        top_p=0.95
    )
    
    print(response.usage)
    output = response.choices[0].message.content
    if not output:
        raise ValueError("GPT call returned no output.")

    return output
