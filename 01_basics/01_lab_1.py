from dotenv import load_dotenv
import os
import boto3
import json



load_dotenv(override=True)

os.environ["AWS_ACCESS_KEY_ID"] = os.getenv('AWS_ACCESS_KEY')
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv('AWS_SECRET_ACCESS_KEY')

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

prompt="Human: Please propose a hard, challenging question to enhance reasoning capability of students. Respond directly with the question without any extra description/explaination like 'Here is the ....','This is the challenging question ....'.\nAssistant:"

body = json.dumps({
    "prompt": prompt ,
    "max_tokens_to_sample": 1000,
    "temperature": 0.7
})

response = bedrock.invoke_model(
    body=body,
    modelId='anthropic.claude-v2', 
    accept='application/json',
    contentType='application/json'
)

question = json.loads(response['body'].read())['completion']
print("Question::",question)

body = json.dumps({
    "prompt": f'Human:{question}.\nAssistant:' ,
    "max_tokens_to_sample": 1000,
    "temperature": 0.7
})

response = bedrock.invoke_model(
    body=body,
    modelId='anthropic.claude-v2', 
    accept='application/json',
    contentType='application/json'
)

response = json.loads(response['body'].read())['completion']
print("Response::",response)