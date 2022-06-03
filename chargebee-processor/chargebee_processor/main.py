import psycopg2
from oep_core.aws import get_body_from_lambda_event
from oep_core.database import get_database_connection
from chargebee_processor.dml import (
    create_oep_customer, is_oep_customer, update_oep_customer,
)
from chargebee_processor.state import (
    handle_chargebee_new_state, handle_go1_state_change,
)


EVENT_TYPES = ['subscription_changed', 'customer_created', 'subscription_created', 'subscription_started', 'subscription_activated',
               'subscription_cancelled', 'subscription_reactivated', 'subscription_renewed', 'subscription_deleted', 'subscription_paused',
               'subscription_resumed']


def handler(event, context):
    print(f'Context: {context}')
    print(f'Event: {event}')

    body = get_body_from_lambda_event(event)

    print(f'Body: {body}')

    event = body.get('event_type')

    connection = None

    if event not in EVENT_TYPES:
        print("Ignoring unrecognised payload")
        return

    print(f"Processing {event.replace('_', ' ')} event")

    try:
        connection = get_database_connection()
        chargebee_customer, oep_customer = process_chargebee_customer(body, connection)
        process_oep_customer(chargebee_customer, oep_customer, connection)
    except psycopg2.Error as exc:
        print(f"Database error processing webhook: {exc}")
        raise
    except Exception as exc:
        print(f"Unexpected error processing webhook: {exc}")
        raise
    else:
        print("Successfully processed Chargebee user mutation")
    finally:  # FIXME: Remove when connection back in context
        if connection:
            print("Closing connection to database")
            connection.close()


def process_chargebee_customer(body, connection):
    chargebee_customer = handle_chargebee_new_state(body)
    oep_customer = is_oep_customer(chargebee_customer.email, connection)
    return chargebee_customer, oep_customer


def process_oep_customer(chargebee_customer, oep_customer, connection):
    if not oep_customer:
        print("Not existing oep customer")
        if not chargebee_customer.go1_active:
            print("Ignoring unknown customer without GO1 access")
        else:
            print("Processing new oep customer with GO1 access")
            create_oep_customer(chargebee_customer, connection)
            handle_go1_state_change(chargebee_customer, 'new')
    else:
        print("Existing oep customer")
        print(f"GO1 active: {chargebee_customer.go1_active}")
        update_oep_customer(chargebee_customer, connection)
        handle_go1_state_change(chargebee_customer, 'update')
