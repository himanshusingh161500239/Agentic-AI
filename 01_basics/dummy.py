import os
import json
from dotenv import load_dotenv
import boto3

load_dotenv(override=True)

os.environ["AWS_ACCESS_KEY_ID"] = os.getenv('AWS_ACCESS_KEY')
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv('AWS_SECRET_ACCESS_KEY')

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')


# First request: generate the question using Claude 3.5 (Messages API)

body = json.dumps({
    "messages": [
        {"role": "user", "content": "Please come up with a challenging, nuanced question that I can ask a number of LLMs to evaluate their intelligence. Answer only with the question, STRICTLY no explanation."}
    ],
    # "thinking": {
    #     "type": "enabled",
    #     "budget_tokens": 4000
    # },
    "max_tokens": 4096,
    "temperature": 0.6,
    "anthropic_version":'bedrock-2023-05-31',
})

response = bedrock.invoke_model(
    body=body,
    modelId='arn:aws:bedrock:us-east-1:269336772098:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0',
    accept='application/json',
    contentType='application/json'
)

question = json.loads(response['body'].read())['content'][0]['text']
print("Question:", question)

