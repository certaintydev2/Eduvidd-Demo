import os

from oep_core.aws import add_to_queue
from oep_core.http_codes import HTTP_INTERNAL_SERVER_ERROR, HTTP_OK

SLACK_WEBHOOK_QUEUE = os.environ.get('SLACK_WEBHOOK_QUEUE')


def handler(event, context):
    """
    We forward all messages to SQS and return 200 to Slack. Slack apps have a 3 second timeout so we
    need to respond in a timely fashion and then do the work asynchronously.
    """
    print(f'Context: {context}')
    print(f'Event: {event}')

    try:
        body = dict(message=event)
        add_to_queue(SLACK_WEBHOOK_QUEUE, body)
    except Exception as exc:
        print(f"Something went wrong sending to SQS: {exc}")
        status_code = HTTP_INTERNAL_SERVER_ERROR
        body = exc
    else:
        status_code = HTTP_OK
        body = 'Successfully received and sent for processing'

    return create_response(status_code, body)


def create_response(status_code, body):
    return dict(
        statusCode=status_code,
        body=body,
    )
