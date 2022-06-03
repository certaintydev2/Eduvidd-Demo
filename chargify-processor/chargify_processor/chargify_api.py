import json
import os

import requests
from oep_core.http_codes import HTTP_NOT_FOUND, HTTP_OK
from oep_core.utils import FIRST

apis = dict(
    cc_api=f'https://{os.environ.get("CHARGIFY_CC_SUB_DOMAIN")}.chargify.com',
    dd_api=f'https://{os.environ.get("CHARGIFY_DD_SUB_DOMAIN")}.chargify.com'
)
usernames = dict(
    cc_username=os.environ.get('CHARGIFY_CC_USERNAME'),
    dd_username=os.environ.get('CHARGIFY_DD_USERNAME')
)
CHARGIFY_PASSWORD = os.environ.get('CHARGIFY_PASSWORD')
GET_TIMEOUT = 10


def get_api_details(obj):
    subdomain = obj.site_subdomain
    suffix = '-dd'
    api = apis.get('dd_api') if suffix in subdomain else apis.get('cc_api')
    username = usernames.get('dd_username') if suffix in subdomain else usernames.get('cc_username')
    return api, username


def chargify_get(url, username):
    return requests.get(url, auth=(username, CHARGIFY_PASSWORD), timeout=GET_TIMEOUT)


# FIXME: just horrible
def lookup_customers_by_email(email):
    print(f"Looking up Chargify customer for email: {email}")
    customers_ids = {}
    all_apis = [apis.get('cc_api'), apis.get('dd_api')]
    all_usernames = [usernames.get('cc_username'), usernames.get('dd_username')]
    for idx, api, in enumerate(all_apis):
        try:
            resp = chargify_get(f"{api}/customers.json?q={email}", all_usernames[idx])
        except requests.RequestException as exc:
            print(f'Lookup subscriptions by email exception: {exc}')
            raise
        else:
            customers = parse_customer_by_email(resp)
            if customers:
                this_api = 'cc' if idx == FIRST else 'dd'
                subdomain_ids = [customer.get('id') for customer in customers]
                customers_ids.setdefault(this_api, []).extend(subdomain_ids)
    print(f"Found records for customer: {customers_ids}")
    return customers_ids


def parse_customer_by_email(resp):
    code = resp.status_code
    text = resp.text
    if code != HTTP_OK:
        msg = 'No customer found' if code == HTTP_NOT_FOUND else f'Get customer error: {text}'
        print(msg)
        return None

    customers = json.loads(text)
    if not customers:
        return None
    return [customer.get('customer') for customer in customers]


def lookup_customer_subscriptions(state):
    print(f"Looking up customer subscriptions for customer ID: {state.customer_id}")
    api, username = get_api_details(state)
    try:
        resp = chargify_get(f"{api}/customers/{state.customer_id}/subscriptions.json", username)
    except requests.RequestException as exc:
        print(f'Lookup customer subscriptions exception: {exc}')
        raise
    else:
        return parse_subscriptions(resp)


def lookup_subscription(state):
    print(f"Looking up subscription for ID: {state.subscription_id}")
    api, username = get_api_details(state)
    try:
        resp = chargify_get(f"{api}/subscriptions/{state.subscription_id}.json", username)
    except requests.RequestException as exc:
        print(f'Lookup subscription exception: {exc}')
        raise
    else:
        return parse_subscriptions(resp)


def parse_subscriptions(resp):
    code = resp.status_code
    text = resp.text
    if code != HTTP_OK:
        msg = (
            'No subscription found' if code == HTTP_NOT_FOUND else f'Get subscription error: {text}'
        )
        print(msg)
        return None

    subscription = json.loads(text)
    if not subscription:
        return None
    if isinstance(subscription, list):
        return [sub.get('subscription') for sub in subscription]
    return subscription.get('subscription')


def lookup_subscription_components(subscription):
    print(f"Looking up components for customer ID: {subscription.customer_id}")
    print(f"Looking up components for subscription ID: {subscription.subscription_id}")
    api, username = get_api_details(subscription)
    try:
        resp = chargify_get(
            f"{api}/subscriptions/{subscription.subscription_id}/components.json", username
        )
    except requests.RequestException as exc:
        print(f'Lookup component exception: {exc}')
        raise
    else:
        return parse_component(resp)


def parse_component(resp):
    code = resp.status_code
    text = resp.text
    if code != HTTP_OK:
        msg = 'No component found' if code == HTTP_NOT_FOUND else f'Get component error: {text}'
        print(msg)
        return None

    components = json.loads(text)
    arrears = [
        comp for comp in components if comp['component']['kind'] == 'quantity_based_component'
        and comp['component']['allocated_quantity'] != 0
    ]
    components = [comp for comp in components if comp['component']['kind'] == 'on_off_component']
    components = [comp for comp in components if comp['component']['enabled']]
    if arrears:
        print(f"Arrears component: {arrears}")
    if not components:
        return None
    return components[FIRST].get('component')
