from openai import OpenAI

client = OpenAI()

def generate_ai_response(prompt):
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )
    return response

