import json
import os

from oep_core.aws import get_body_from_lambda_event
from oep_core.slack import send_to_slack
from oep_core.utils import FIRST

SLACK_DEAD_LETTER_URL = os.environ.get('SLACK_DEAD_LETTER_URL')


SUBSCRIPTION_NEW_STATE = 'subscription_created'
SUBSCRIPTION_UPDATE_STATE = ['subscription_changed', 'subscription_started', 'subscription_activated','subscription_cancelled',
                             'subscription_reactivated', 'subscription_renewed', 'subscription_deleted',
                             'subscription_paused', 'subscription_resumed']

SUBSCRIPTION_KEYS = [
    'id',
    'status',
    'customer_id',
    'first_name',
    'last_name',
    'email',
]

GO1_NEW_KEYS = [
    'kind',
    'first_name',
    'last_name',
    'email',
]
GO_UPDATE_KEYS = [
    'kind',
    'email',
    'state',
]


def handler(event, context):
    print(f'Context: {context}')
    print(f'Event: {event}')

    content, kind = parse_body(event)
    print(f'Content: {content}')
    print(f'Kind: {kind}')

    if not content:
        return
    payload = format_for_slack(content, kind)
    print(f'Payload: {payload}')
    send_to_slack(SLACK_DEAD_LETTER_URL, payload)


def parse_body(event):
    body = get_body_from_lambda_event(event)
    content = dict()
    keys = None
    active = None
    kind = None
    states = [SUBSCRIPTION_NEW_STATE] + SUBSCRIPTION_UPDATE_STATE
    if 'event_type' in body and body.get('event_type') in states:
        event_type = body.get('event_type')
        if event_type == SUBSCRIPTION_NEW_STATE:
            keys = SUBSCRIPTION_KEYS
            active = body.get('content')['subscription']['status'] == 'active'
            kind = 'Chargebee New Subscription'
        elif event_type in SUBSCRIPTION_UPDATE_STATE:
            keys = SUBSCRIPTION_KEYS
            active = body.get('content')['subscription']['status'] == 'active'
            kind = 'Chargebee Updated Subscription'
        else:
            print("Unrecognised Chargebee event type")
    else:
        event = body.get('kind')
        if event == 'new':
            keys = GO1_NEW_KEYS
            active = True
            kind = 'GO1 New Customer'
        elif event == 'update':
            keys = GO_UPDATE_KEYS
            active = True
            kind = 'GO1 Update Customer'
        else:
            print("Unrecognised GO1 event type")

    if not keys or not active:
        print("No action")
        return content, kind

    for k, v in body.items():
        if k == "content":
            for k1, v1 in v.items():
                if k1 in ["subscription", "customer"]:
                    for k2, v2 in v1.items():
                        if k2 in keys:
                            if k1 == "subscription" and k2 == "id":
                                content["subscription_id"] = v2
                            else:
                                content[k2] = v2
        if k in keys and 'GO1' in kind:
            content[k] = v
    return content, kind


def format_for_slack(content, kind):
    return [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'<!channel> {kind} dead letter from SQS :skull: :envelope:'
            }
        },
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'```{json.dumps(content, indent=4)}```',
            }
        }
    ]
