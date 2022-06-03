import base64
import datetime
import hashlib
import hmac
import json
import os
import time
from io import BytesIO

import boto3
import botocore.exceptions
import pandas as pd
from oep_core.aws import get_body_from_lambda_event
from oep_core.database import get_database_connection
from oep_core.slack import send_to_slack
from oep_core.utils import FIRST, FIVE, ONE_HOUR, ONE_MINUTE
from pytz import timezone

TIME_NOW = datetime.datetime.now(tz=timezone(os.environ.get('TIMEZONE', 'Australia/Brisbane')))
SLACK_REPORTING_URL = os.environ.get('SLACK_REPORTING_URL')
SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET')
BUCKET = os.environ.get('REPORTING_BUCKET')
CLIENT = boto3.client('s3')
ACTIVE = 1
INACTIVE = 0
INDEX_OFFSET = 1


def handler(event, context):
    print(f'Context: {context}')
    print(f'Event: {event}')

    body = get_body_from_lambda_event(event)

    try:
        check_signature(body)
        customers, metadata = build_objects()
        payload = transfer_to_storage(customers)
        payload.update(dict(metadata=metadata))
        slack_payload = format_for_slack(payload)
        send_to_slack(SLACK_REPORTING_URL, slack_payload)
    except Exception as exc:
        print(f"Unexpected error processing webhook: {exc}")
        raise
    else:
        print("Successfully processed user reporting")


def check_signature(body):
    print("Checking signature")
    message = body.get('message')
    headers = message.get('headers')
    timestamp = int(headers.get('x-slack-request-timestamp'))
    # The request timestamp is more than five minutes from local time. It could be a replay attack.
    if abs(time.time() - timestamp) > FIVE * ONE_MINUTE:
        print("Possible replay attack")
        raise Exception("Unauthorised request")

    request_body = base64.b64decode(message.get('body')).decode('utf-8')
    secret = SLACK_SIGNING_SECRET.encode('utf-8')
    basestring = f'v0:{timestamp}:{request_body}'.encode('utf-8')
    signature = hmac.new(secret, basestring, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(f'v0={signature}', headers.get('x-slack-signature')):
        print("Signature does not match")
        raise Exception("Unauthorised request")


def build_objects():
    customers = build_customers()
    metadata = build_metadata(customers)
    customers = create_file_object(customers)
    return customers, metadata


def build_customers():
    return pd.read_sql_query(
        """
            select first_name, last_name, email, subdomain, go1_active as oep_active,
            go1_id as oep_id, user_type, created_at, updated_at
            from customers
        """, con=get_database_connection()
    )


def build_metadata(df):
    active = len(df[(df['user_type'] == 'user') & (df['oep_active'] == ACTIVE)])
    inactive = len(df[(df['user_type'] == 'user') & (df['oep_active'] == INACTIVE)])
    external = len(df[(df['user_type'] == 'external')])
    fake = len(df[(df['user_type'] == 'fake')])
    print(f"Active: {active}")
    print(f"Inactive: {inactive}")
    print(f"Free: {external}")
    print(f"Fake: {fake}")
    print(f"Total: {active + inactive + external + fake}")
    return dict(
        active=active,
        inactive=inactive,
        external=external,
        fake=fake,
    )


def create_file_object(customers):
    customers.index = customers.index + INDEX_OFFSET
    customers.index.names = ['number']
    customers = customers.to_csv(sep=',', index=True).encode('utf-8')
    return BytesIO(customers)


def transfer_to_storage(obj):
    filename = 'customers.csv'
    object_key = f'{TIME_NOW.strftime("%Y-%m-%d-%H-%M-%S")}/{filename}'
    upload_to_s3(CLIENT, BUCKET, object_key, obj)
    presigned_url = build_presigned_url(CLIENT, object_key)
    return {filename.split('.')[FIRST]: presigned_url}


def upload_to_s3(client, bucket, object_key, file_obj):
    """
    Uploads bytes objects to S3.

    :param client: boto3 client
    :param bucket: String of bucket name
    :param object_key: Full object name and "directories" in its path
    :param file_obj: BytesIO object containing data to upload
    """
    try:
        client.upload_fileobj(Bucket=bucket, Key=object_key, Fileobj=file_obj)
    except botocore.exceptions.ClientError as err:
        print(f"Error uploading to S3: {err}")
        raise err
    else:
        print("S3 data uploaded")


def build_presigned_url(client, key):
    return client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': BUCKET,
            'Key': key,
        },
        ExpiresIn=ONE_HOUR,
    )


def format_for_slack(body):
    return [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*Summary of users*\n```{json.dumps(body.get("metadata"), indent=4)}```',
            }
        },
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'CSV file of <{body.get("customers")}|users>',
            }
        },
    ]
