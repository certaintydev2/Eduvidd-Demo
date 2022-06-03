import psycopg2
from oep_core.aws import get_body_from_lambda_event
from oep_core.database import get_database_connection
from oep_core.utils import FIRST

from chargify_processor.chargify_api import lookup_subscription
from chargify_processor.dml import (
    create_oep_customer, is_oep_customer, update_oep_customer,
)
from chargify_processor.state import (
    Subscription, handle_chargify_new_state, handle_go1_state_change,
)

EVENT_TYPES = [
    'signup_success',
    'subscription_state_change',
    'component_allocation_change',
]


def handler(event, context):
    print(f'Context: {context}')
    print(f'Event: {event}')

    body = get_body_from_lambda_event(event)
    event = body.get('event')
    event = event[FIRST]
    connection = None

    if event not in EVENT_TYPES:
        print("Ignoring unrecognised payload")
        return

    print(f"Processing {event.replace('_', ' ')} event")
    if event == 'component_allocation_change':
        body = pre_process_component(body)
    try:
        connection = get_database_connection()
        chargify_customer, oep_customer = process_chargify_customer(body, connection)
        process_oep_customer(chargify_customer, oep_customer, connection)
    except psycopg2.Error as exc:
        print(f"Database error processing webhook: {exc}")
        raise
    except Exception as exc:
        print(f"Unexpected error processing webhook: {exc}")
        raise
    else:
        print("Successfully processed Chargify user mutation")
    finally:  # FIXME: Remove when connection back in context
        if connection:
            print("Closing connection to database")
            connection.close()


def process_chargify_customer(body, connection):
    chargify_customer = handle_chargify_new_state(body)
    oep_customer = is_oep_customer(chargify_customer.email, connection)
    return chargify_customer, oep_customer


def process_oep_customer(chargify_customer, oep_customer, connection):
    if not oep_customer:
        print("Not existing oep customer")
        if not chargify_customer.go1_active:
            print("Ignoring unknown customer without GO1 access")
        else:
            print("Processing new OEP customer with GO1 access")
            create_oep_customer(chargify_customer, connection)
            handle_go1_state_change(chargify_customer, 'new')
    else:
        print("Existing OEP customer")
        print(f"GO1 active: {chargify_customer.go1_active}")
        update_oep_customer(chargify_customer, connection)
        handle_go1_state_change(chargify_customer, 'update')


def pre_process_component(body):
    subscription_id = body.get('payload[subscription][id]')[FIRST]
    site_subdomain = body.get('payload[site][subdomain]')[FIRST]
    state = Subscription(subscription_id=subscription_id, site_subdomain=site_subdomain)
    sub = lookup_subscription(state)
    body['payload[subscription][customer][email]'] = [sub.get('customer').get('email')]
    body['payload[subscription][customer][first_name]'] = [sub.get('customer').get('first_name')]
    body['payload[subscription][customer][last_name]'] = [sub.get('customer').get('last_name')]
    return body
