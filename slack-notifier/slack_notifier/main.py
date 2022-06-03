import json
import os

from oep_core.aws import get_body_from_lambda_event
from oep_core.slack import send_to_slack
from oep_core.utils import FIRST

SLACK_DEAD_LETTER_URL = os.environ.get('SLACK_DEAD_LETTER_URL')
SIGNUP_STATE = 'signup_success'
SUBSCRIPTION_STATE = 'subscription_state_change'
COMPONENT_STATE = 'component_allocation_change'
SIGNUP_KEYS = [
    'payload[subscription][customer][email]',
    'payload[subscription][customer][first_name]',
    'payload[subscription][customer][last_name]',
    'payload[subscription][customer][id]',
    'payload[subscription][id]',
    'payload[subscription][previous_state]',
    'payload[subscription][state]',
    'payload[site][subdomain]',
]
SUBSCRIPTION_KEYS = [
    'payload[subscription][id]',
    'payload[subscription][state]',
    'payload[subscription][previous_state]',
    'payload[subscription][customer][id]',
    'payload[subscription][customer][first_name]',
    'payload[subscription][customer][last_name]',
    'payload[subscription][customer][email]',
    'payload[site][subdomain]',
]
COMPONENT_KEYS = [
    'payload[subscription][state]',
    'payload[subscription][id]',
    'payload[subscription][name]',
    'payload[previous_allocation]',
    'payload[new_allocation]',
    'payload[component][unit_name]',
    'payload[site][subdomain]',
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
    if not content:
        return
    payload = format_for_slack(content, kind)
    send_to_slack(SLACK_DEAD_LETTER_URL, payload)


def parse_body(event):
    body = get_body_from_lambda_event(event)
    content = dict()
    keys = None
    active = None
    kind = None
    states = [SIGNUP_STATE, SUBSCRIPTION_STATE, COMPONENT_STATE]
    if 'event' in body and body.get('event')[FIRST] in states:
        event = body.get('event')[FIRST]
        if event == SIGNUP_STATE:
            keys = SIGNUP_KEYS
            active = body.get('payload[subscription][state]')[FIRST] == 'active'
            kind = 'Chargify New Subscription'
        elif event == SUBSCRIPTION_STATE:
            keys = SUBSCRIPTION_KEYS
            active = body.get('payload[subscription][state]')[FIRST] == 'active'
            kind = 'Chargify Updated Subscription'
        elif event == COMPONENT_STATE:
            keys = COMPONENT_KEYS
            active = body.get('payload[new_allocation]')[FIRST] == '1'
            kind = 'Chargify Updated Component'
        else:
            print("Unrecognised Chargify event type")
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
        if k in keys:
            content[k] = v if 'GO1' in kind else v[FIRST]
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
