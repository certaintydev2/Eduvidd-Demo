
import os
import chargebee
import requests


# Environment required for chargebee
SITE_KEY = os.environ.get('CHARGEBEE_SITE_KEY')
SITE_URL = os.environ.get('CHARGEBEE_SITE_URL')

# configuring chargebee object
chargebee.configure(SITE_KEY, SITE_URL)


def lookup_customer_subscriptions(state):
    print(f"Looking up customer subscriptions for customer ID: {state.customer_id}")

    try:
        subscriptions = chargebee.Subscription.list({"customer_id[is]": str(state.customer_id)}).__dict__['response']
    except requests.RequestException as exc:
        print(f'Lookup customer subscriptions exception: {exc}')
        raise

    else:
        return subscriptions