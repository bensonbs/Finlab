import os
import openai

def chat_gpt(prompt):
    
    openai.api_key = os.environ['OPENAI_API_KEY']
    
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    
    ai_response = response['choices'][0]['message']['content']

    return ai_response