import json

import boto3
from botocore.exceptions import BotoCoreError

from oep_core.utils import FIRST


def add_to_queue(queue, body):
    print(f"Adding to {queue} user queue")
    print(f"Body: {body}")
    client = boto3.client('sqs')
    try:
        response = client.send_message(
            QueueUrl=queue,
            MessageBody=json.dumps(body)
        )
    except BotoCoreError as err:
        print(f'Exception putting task in SQS: {err}')
        print(body)
        raise
    else:
        md5 = response.get('MD5OfMessageBody')
        message_id = response.get('MessageId')
        print("Successfully sent message to SQS")
        print(f"MD5: {md5}")
        print(f"MessageID: {message_id}")


def get_body_from_lambda_event(event):
    record = event.get('Records')[FIRST] 
    return json.loads(record.get('body'))
