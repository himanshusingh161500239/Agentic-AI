import os
import json
from dotenv import load_dotenv
import boto3
import google.generativeai as genai

load_dotenv(override=True)

os.environ["AWS_ACCESS_KEY_ID"] = os.getenv('AWS_ACCESS_KEY')
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv('AWS_SECRET_ACCESS_KEY')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')


google_access_key=os.getenv('GEMINI_ACCESS_KEY')
genai.configure(api_key=google_access_key)
model = genai.GenerativeModel("gemini-1.5-flash")

competitors=[]
answers=[]


## Question generation ##
prompt="Human: Please come up with a challenging, nuanced question that I can ask a numember of LLM's to evaluate their intelligence. Answer only with the question,STRICLTY no explaination.\nAssistant:"
body = json.dumps({
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 4096,
    "temperature": 0.3,
    "anthropic_version":'bedrock-2023-05-31',
})
competitors.append("anthropic.claude-3-5-sonnet")
response = bedrock.invoke_model(
    body=body,
    modelId='arn:aws:bedrock:us-east-1:269336772098:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0',
    accept='application/json',
    contentType='application/json'
)
question = json.loads(response['body'].read())['content'][0]['text']
# print("Question:", question)


## Response generation using sonnet 3.5 ##
response = bedrock.invoke_model(
    body=body,
    modelId='arn:aws:bedrock:us-east-1:269336772098:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0',
    accept='application/json',
    contentType='application/json'
)
sonnet_response = json.loads(response['body'].read())['content'][0]['text']
# print("Sonnet Response", sonnet_response)
answers.append(sonnet_response)


## Response generation using sonnet 3.5 ##
competitors.append("gemini-1.5-flash")
gemini_response = model.generate_content(question)
# print("Answer::",response.text)
answers.append(gemini_response.text)


# print("Competitors::",competitors)
# print("Responses::",answers)


## let's compare ##

together=""
for index, answer in enumerate(answers):
    together+= f'# Response from competetior {index+1}\n\n'
    together+=answer + '\n\n'


judge=f"""
    You are judging a competition between {len(competitors)} competitors.
    Each modle has been given this questions:
    {question}
    Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.
    Respond with JSON, and only JSON, with the following format:
    {{"results":["best competitor number","second best competitor number","third best competitor number",......]}}

    Here are the responses from each competitor:
    {together}

    Now respond with the JSON with the ranked order of the competitors, nothing else. Do not include markdown formatting or code blocks.
"""

body = json.dumps({
    "messages": [
        {"role": "user", "content": judge}
    ],
    "max_tokens": 4096,
    "temperature": 0.3,
    "anthropic_version":'bedrock-2023-05-31',
})
competitors.append("anthropic.claude-3-sonnet")
response = bedrock.invoke_model(
    body=body,
    modelId='arn:aws:bedrock:us-east-1:269336772098:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0',
    accept='application/json',
    contentType='application/json'
)
comparision_response = json.loads(response['body'].read())['content'][0]['text']

result_dict=json.loads(comparision_response)
ranks = result_dict["results"]
for index,result in enumerate(ranks):
    competitor =competitors[int(result)-1]
    print(f"Rank {index+1}: {competitor}")
