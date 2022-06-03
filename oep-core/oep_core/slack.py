import requests

from oep_core.http_codes import HTTP_OK


def send_to_slack(slack_webhook_url, payload):
    try:
        resp = requests.post(slack_webhook_url, json=dict(blocks=payload))
    except Exception as exc:
        print(f"Exception sending webhook to Slack: {exc}")
        print(payload)
    else:
        if resp.status_code != HTTP_OK:
            print(f"Error sending webhook to Slack: {resp.text}")
            print(payload)
        print("Successfully sent webhook to Slack")
