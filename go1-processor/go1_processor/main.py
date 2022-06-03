import json
import os
from datetime import datetime

import requests
from oep_core.aws import get_body_from_lambda_event
from oep_core.database import execute_cursor, get_database_connection
from oep_core.http_codes import HTTP_CREATED, HTTP_OK
from oep_core.utils import FIRST

GO1_API = 'https://api.go1.com/v2'
GO1_AUTH = 'https://auth.go1.com/oauth'
GO1_CLIENT_ID = os.environ.get('GO1_CLIENT_ID')
GO1_CLIENT_SECRET = os.environ.get('GO1_CLIENT_SECRET')


def handler(event, context):
    print(f'Context: {context}')
    print(f'Event: {event}')

    body = get_body_from_lambda_event(event)
    kind = body.get('kind')
    token = get_token()
    connection = get_database_connection()
    print(f"Body: {body}")
    try:
        if kind == 'new':
            user = create_go1_user(body, token)
            update_oep_user(user, connection)
        elif kind == 'update':
            body['go1_id'] = get_oep_user(body)
            if body['go1_id'] is not None:
                body['go1_id'] = body['go1_id'][FIRST]
                update_go1_user(body, token)
        else:
            print("Ignoring unrecognised payload")
    except Exception as exc:
        print(f"Unexpected error processing GO1 user: {exc}")
        raise
    else:
        print("Successfully processed GO1 user mutation")


def get_token():
    data = dict(
        client_id=GO1_CLIENT_ID,
        client_secret=GO1_CLIENT_SECRET,
        grant_type='client_credentials',
    )
    try:
        resp = requests.post(f'{GO1_AUTH}/token', data=data)
    except requests.RequestException as exc:
        print(f'Get token exception: {exc}')
        raise
    else:
        if resp.status_code != HTTP_OK:
            print(f'Get token error: {resp.text}')
            raise Exception("Cannot get access token")
        response = json.loads(resp.text)
        return response.get('access_token')


def create_go1_user(body, token):
    print("Creating GO1 user")
    headers = dict(Authorization=f'Bearer {token}')
    data = dict(
        email=body.get('email'),
        first_name=body.get('first_name'),
        last_name=body.get('last_name'),
        roles=['Learner']
    )
    try:
        resp = requests.post(f'{GO1_API}/users', headers=headers, json=data)
    except requests.RequestException as exc:
        print(f'Create GO1 user exception: {exc}')
        raise
    else:
        if resp.status_code != HTTP_CREATED:
            print(f'Create GO1 user error: {resp.text}')
            raise Exception("Cannot create GO1 user")
        user = json.loads(resp.text)
        return user


def update_go1_user(body, token):
    print(f"Updating GO1 user: {body.get('go1_id')}")
    headers = dict(Authorization=f'Bearer {token}')
    data = dict(
        status=body.get('state'),
    )
    try:
        resp = requests.patch(f"{GO1_API}/users/{body.get('go1_id')}", headers=headers, json=data)
    except requests.RequestException as exc:
        print(f'Update GO1 user exception: {exc}')
        raise
    else:
        if resp.status_code != HTTP_OK:
            print(f'Update GO1 user error: {resp.text}')
            raise Exception("Cannot update GO1 user")


def update_oep_user(user, connection):
    print(f"Updating GO1 ID: {user.get('id')}")
    time_now = datetime.utcnow()
    sql = """
        UPDATE customers
        SET go1_id = %(go1_id)s, updated_at = %(updated_at)s
        WHERE email = %(email)s
    """
    values = (dict(go1_id=user.get('id'), updated_at=time_now, email=user.get('email')))
    execute_cursor(sql, values, connection)


def get_oep_user(body):
    print(f"Getting GO1 customer ID for email: {body.get('email')}")
    sql = """
        SELECT go1_id
        FROM customers
        WHERE email = %(email)s
    """
    values = (dict(email=body.get('email')))
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute(sql, values)
    result = cursor.fetchone()
    cursor.close()
    return result
