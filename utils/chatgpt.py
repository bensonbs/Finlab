def chat_gpt(prompt):
    
    openai.api_key = config["openai_api_key"]
    
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    
    ai_response = response['choices'][0]['message']['content']

    return ai_response