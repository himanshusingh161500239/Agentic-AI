import openai

# Set up your Azure OpenAI credentials
openai.api_type='azure'
openai.api_key= "bfe2e929482740698518ec2da3efe87c"
openai.azure_endpoint="https://openapi-gpt4-pocs.openai.azure.com/"
openai.api_version = "2025-01-01-preview"

response = openai.chat.completions.create(
    # model="gpt-35-turbo",
    model="gpt4poc",
    temperature=0.5,
    max_tokens=4000,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Please come up with a challenging, nuanced question that I can ask a numember of LLM's to evaluate their intelligence. Answer only with the question,STRICLTY no explaination"}
    ]
)
print(response.choices[0].message.content)
