from slack_webhook.main import handler

if __name__ == '__main__':
    the_event = None
    the_context = None
    resp = handler(the_event, the_context)
