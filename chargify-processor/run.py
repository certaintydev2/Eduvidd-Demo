import json

from chargify_processor.main import handler

if __name__ == '__main__':
    # TODO: convert to unit tests
    # Signup
    # sqs_stuff = dict({
    #     'id': ['712441715'],
    #     'event': ['signup_success'],
    #     'payload[subscription][customer][email]': ['hannah@horvath.com'],
    #     'payload[subscription][customer][first_name]': ['Hannah'],
    #     'payload[subscription][customer][last_name]': ['Horvath'],
    #     'payload[subscription][customer][id]': ['34501447'],
    #     'payload[subscription][id]': ['33421031'],
    #     'payload[subscription][previous_state]': ['inactive'],
    #     'payload[subscription][state]': ['active'],
    #     'payload[site][subdomain]': ['professional-association-cc-dev']
    # })

    # Subscription
    sqs_stuff = dict({
        'id': ['709852146'], 'event': ['subscription_state_change'],
        'payload[subscription][customer][email]': ['hannah@horvath.com'],
        'payload[subscription][customer][first_name]': ['Hannah'],
        'payload[subscription][customer][last_name]': ['Horvath'],
        'payload[subscription][customer][id]': ['34501447'],
        'payload[subscription][id]': ['33421031'],
        'payload[subscription][previous_state]': ['inactive'],
        'payload[subscription][state]': ['active'],
        'payload[site][subdomain]': ['professional-association-cc-dev']
    })

    # Component
    # sqs_stuff = dict({
    #     'id': ['710370003'],
    #     'event': ['component_allocation_change'],
    #     'payload[subscription][id]': ['33421031'],
    #     'payload[subscription][name]': ['Hannah Horvath'],
    #     'payload[component][kind]': ['quantity_based_component'],
    #     'payload[component][id]': ['190702'],
    #     'payload[component][name]': ['CPD Annually'],
    #     'payload[component][unit_name]': ['on/off'],
    #     'payload[previous_allocation]': ['0'],
    #     'payload[new_allocation]': ['1'],
    #     'payload[memo]': ['Customer requested 3 bananas.'],
    #     'payload[site][subdomain]': ['professional-association-cc-dev']
    # })

    the_event = dict(
        Records=[dict(body=json.dumps(sqs_stuff))],
    )
    the_context = None
    resp = handler(the_event, the_context)
    # print(resp)
