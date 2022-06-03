import json

from user_reporting.main import handler

if __name__ == '__main__':
    slack_payload = {
        'message': {
            'headers': {
                'x-slack-request-timestamp': '1594209964',
                'x-slack-signature':
                    ''
            },
            'body':
                (
                    ''
                ),
            'isBase64Encoded': True
        }
    }
    the_event = dict(
        Records=[dict(body=json.dumps(slack_payload))],
    )
    the_context = None
    resp = handler(the_event, the_context)
