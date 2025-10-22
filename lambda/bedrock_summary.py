import boto3, json, os
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=os.environ["AWS_REGION"])

RANKINGS_TABLE = os.environ["RANKINGS_TABLE_NAME"]
KNOWLEDGE_BASE_ID = os.environ["KB_ID"]

def handler(event, context):
    table = dynamodb.Table(RANKINGS_TABLE)
    rankings = table.scan()["Items"]
    
    for r in rankings:
        for k, v in r.items():
            if isinstance(v, Decimal):
                r[k] = float(v)
    
    summaries = []
    for r in rankings:
        team = r["team"]
        score = r.get("sentiment_score", 0)
        prompt = build_prompt(team, score)
        summary_text = call_knowledge_base(prompt)
        summaries.append({"team": team, "summary": summary_text})
    
    print(json.dumps(summaries, indent=2))
    return {"summaries": summaries}


def build_prompt(team, score):
    return f"""
Summarize the fan sentiment for the {team} based on recent Reddit discussions available in the knowledge base.

Sentiment score (from data analysis): {score:.2f}

Write a short, well-structured summary (1–2 paragraphs) describing:
- The emotional tone (optimistic, angry, excited, disappointed, etc.)
- Key discussion topics or trends among fans
- Any noticeable patterns or shifts in attitude over the last few days.
"""


def call_knowledge_base(prompt):
    response = bedrock_agent.retrieve_and_generate(
        input={"text": prompt},
        retrieveAndGenerateConfiguration={
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
            },
            "type": "KNOWLEDGE_BASE"
        }
    )
    
    output_text = response.get("output", {}).get("text", "")
    return output_text
