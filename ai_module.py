from groq import Groq
from openai import OpenAI
import ollama
import keys, config

if config.AI == "groq":
    groq_client = Groq(api_key=keys.GROQ_API_KEY)
elif config.AI == "openai":
    openai_client = OpenAI(api_key=keys.OPENAI_API_KEY)
else:
    ollama.chat(
        model=config.AI,
        messages=[{"role": "system", "content": "Preload model"}]
    )




def generate(history):
    if config.AI == "groq":
        output = groq(history)
    elif config.AI == "openai":
        output = gpt(history)
    else:
        output = local(history, config.AI)
    return output
        


def groq(history):
    chat_completion = groq_client.chat.completions.create(
            messages=history, # type: ignore
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
    )
    ai_output = chat_completion.choices[0].message.content
    total_tokens = chat_completion.usage.total_tokens# type: ignore
    return str(ai_output)

def gpt(history):
    completion = openai_client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=history
    )

    return str(completion.choices[0].message.content)

def local(history, model):
    response = ollama.chat(model=model, messages=history)
    return str(response["message"]["content"])
    