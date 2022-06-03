import os

import psycopg2


def get_database_connection():
    print("Getting database connection")
    try:
        connection = psycopg2.connect(
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT'),
            database=os.environ.get('DB_DATABASE'),
        )
    except psycopg2.Error as exc:
        print(f"Error getting database connection: {exc}")
        raise
    else:
        return connection


def execute_cursor(sql, values, connection):
    print("Executing cursor")
    print(f"SQL {sql}")
    print(f"Values: {values}")
    try:
        cursor = connection.cursor()
        cursor.execute(sql, values)

    except psycopg2.Error as exc:
        print(f"Error executing cursor: {exc}")
        raise
    else:
        print("Writing to database")
        connection.commit()
        cursor.close()
