import boto3, os


bedrock = boto3.client("bedrock-agent")
def handler(event, context):
    kb_id = os.environ.get("KB_ID")
    data_source = os.getenv("DATA_SOURCE_ID")
    bedrock.start_ingestion_job(knowledgeBaseId=kb_id, dataSourceId=data_source)
    print(f"Triggered KB re-sync for {kb_id}")