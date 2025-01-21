import os
from dotenv import load_dotenv

from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def run_completion(prompt, label):
    messages = [{"role": "user", "content": prompt}]
    print(f"    RunningLLM({label})")
    completion = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=messages,
    )
    return completion.choices[0].message.content
