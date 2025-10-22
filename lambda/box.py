import boto3 
import tarfile
import os
import tempfile
import json


def handler(event, lambda_context):
    s3_client = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.getenv("RANKINGS_TABLE_NAME"))
    bucket_name = os.environ["OUTPUT_BUCKET_NAME"]
    my_key = event.get("key", "myFile.tar.gz")

    temp_dir = tempfile.mkdtemp()
    local_path = os.path.join(temp_dir, os.path.basename(my_key))
    get_path = os.path.join(temp_dir, "extracted")
    os.makedirs(get_path, exist_ok=True)

    s3_client.download_file(bucket_name, my_key, local_path)

    with tarfile.open(local_path, mode="r:gz") as tar_file:
        tar_file.extractall(path=get_path)

    count = 0
    score_sum = 0

    team_dict = {}
    for filename in os.listdir(get_path):
        file_path = os.path.join(get_path, filename)
        if not filename.endswith(".out"):
            continue
        with open(file_path, "r") as file:
                    data = json.load(file)
        # entities = data.get("Entities", [])
        mentions = data.get("Mentions", [])
        # for i in entities:
        for ment in mentions:                
            org = ment.get("Type")

            if org != "ORGANIZATION":
                continue

            name = ment.get("Text")
            if not name:
                continue
            sentiment = ment.get("MentionSentiment", {}).get("SentimentScore", {})
            neg_score = float(sentiment.get("Negative", 0))
            pos_score = float(sentiment.get("Positive", 0))
            
            negative = False
            if abs(neg_score) > abs(pos_score):
                score = neg_score
                negative = True
            else:
                score = pos_score

            if negative:
                score = -score
            tuple = (0,0)
            if org in team_dict:
                tuple = team_dict[org]

            tuple = (tuple[0] + score, tuple[1] + 1)
            
            team_dict[org] = tuple

    for key, value in team_dict:
        count = value[1]
        score = value[0]
        print(f"Key: {key}, Value: {value}")
        avg = 0 if count == 0 else score_sum / count

        table.put_item(
             Item = {
                  'team': key,
                  'Score': avg
             }
        )
                