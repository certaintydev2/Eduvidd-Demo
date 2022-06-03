import json

from go1_processor.main import handler

if __name__ == '__main__':
    # Signup
    # sqs_stuff = dict(
    #     {
    #         'kind': 'new',
    #         'first_name': 'Hannah',
    #         'last_name': 'Horvath',
    #         'email': 'hannah@horvath.com',
    #     }
    # )

    # sqs_stuff = dict(
    #     {
    #         'kind': 'update',
    #         'email': 'hannah@horvath.com',
    #         'state': True,
    #     }
    # )

    the_event = dict(
        Records=[dict(body=json.dumps(sqs_stuff))],
    )
    the_context = None
    resp = handler(the_event, the_context)
