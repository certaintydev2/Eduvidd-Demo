import os
from dataclasses import dataclass
from typing import Optional
from oep_core.aws import add_to_queue

from chargebee_processor.chargebee_api import lookup_customer_subscriptions

GO1_USER_QUEUE = os.environ.get('GO1_USER_QUEUE')


@dataclass
class State:
    customer_id: Optional[int] = None
    email: Optional[str] = None


@dataclass
class Customer:
    first_name: str
    last_name: str
    email: str
    subdomain: str = 'npaq'
    go1_active: Optional[bool] = None
    user_type: str = 'user'


def parse_body(kind, body):
    return body.get("content")['customer'][kind]


def handle_chargebee_new_state(body):
    state = State(email=parse_body('email', body), customer_id=parse_body('id', body))

    subscriptions = lookup_customer_subscriptions(state)

    subscription_valid = []
    component_valid = []

    for subscription in subscriptions:
        subscription_valid.append(True if subscription.get('subscription').get('status') == 'active' else False)
        has_component = [plans['item_price_id'] for plans in subscription.get('subscription').get('subscription_items')
                         if plans['item_type'] == "addon"]
        for i in has_component:
            component_valid.append(True if "CPD" in i.upper() else False)
    has_valid_subscription = any(subscription_valid)
    has_valid_component = any(component_valid)
    has_go1_access = all([has_valid_subscription, has_valid_component])

    return Customer(
        first_name=parse_body('first_name', body),
        last_name=parse_body('last_name', body),
        email=state.email.lower(),
        go1_active=has_go1_access,
    )


def handle_go1_state_change(customer, kind):
    if kind == 'new':
        go1_user = dict(
            kind=kind,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email.lower(),
        )
    else:
        go1_user = dict(
            kind=kind,
            email=customer.email.lower(),
            state=customer.go1_active,
        )
    add_to_queue(GO1_USER_QUEUE, go1_user)
