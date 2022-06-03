import os
from dataclasses import dataclass
from typing import Optional

from oep_core.aws import add_to_queue
from oep_core.utils import FIRST

from chargify_processor.chargify_api import (
    lookup_customer_subscriptions, lookup_customers_by_email, lookup_subscription_components,
)

GO1_USER_QUEUE = os.environ.get('GO1_USER_QUEUE')


@dataclass
class State:
    customer_id: Optional[int] = None
    email: Optional[str] = None
    site_subdomain: Optional[str] = None


@dataclass
class Subscription:
    customer_id: Optional[int] = None
    subscription_id: Optional[int] = None
    site_subdomain: Optional[str] = None


@dataclass
class Customer:
    first_name: str
    last_name: str
    email: str
    subdomain: str = 'npaq'
    go1_active: Optional[bool] = None
    user_type: str = 'user'


def parse_body(kind, body):
    return body.get(f'payload[subscription][customer][{kind}]')[FIRST]


def handle_chargify_new_state(body):
    state = State(email=parse_body('email', body))
    domain_subscriptions = handle_all_subscriptions(state.email)
    subscription_valid = []
    component_valid = []
    for domain, subscriptions in domain_subscriptions.items():
        for subscription in subscriptions:
            subscription_valid.append(True if subscription.get('state') == 'active' else False)
            this_subscription = Subscription(
                customer_id=subscription.get('customer').get('id'),
                subscription_id=subscription.get('id'),
                site_subdomain=f'-{domain}'
            )
            has_component = lookup_subscription_components(this_subscription)
            component_valid.append(True if has_component else False)
    has_valid_subscription = any(subscription_valid)
    has_valid_component = any(component_valid)
    has_go1_access = all([has_valid_subscription, has_valid_component])

    return Customer(
        first_name=parse_body('first_name', body),
        last_name=parse_body('last_name', body),
        email=state.email.lower(),
        go1_active=has_go1_access,
    )


def handle_all_subscriptions(email):
    customer_metadata = lookup_customers_by_email(email)
    subscriptions = dict()
    for site_subdomain, customer_ids in customer_metadata.items():
        for customer_id in customer_ids:
            state = State(customer_id=customer_id, site_subdomain=f'-{site_subdomain}')
            domain_subscription = lookup_customer_subscriptions(state)
            if domain_subscription:
                subscriptions.setdefault(site_subdomain, []).extend(domain_subscription)
    return subscriptions


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
