from datetime import datetime

from oep_core.database import execute_cursor


def is_oep_customer(email, connection):
    print(f"Checking if OEP customer exists for email: {email}")
    sql = """
        SELECT id, email
        FROM customers
        WHERE email = %(email)s
    """
    values = (dict(email=email))
    cursor = connection.cursor()
    cursor.execute(sql, values)
    result = cursor.fetchone()
    cursor.close()
    return result


def create_oep_customer(customer, connection):
    print(f"Creating OEP customer for email: {customer.email}")
    created_at = updated_at = datetime.utcnow()
    sql = """
        INSERT INTO customers(
            first_name, last_name, email, subdomain, go1_active,
            user_type, created_at, updated_at
        )
        VALUES (
            %(first_name)s, %(last_name)s, %(email)s, %(subdomain)s, %(go1_active)s,
            %(user_type)s, %(created_at)s, %(updated_at)s
        );
    """
    values = (
        dict(
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            subdomain=customer.subdomain,
            go1_active=customer.go1_active,
            user_type=customer.user_type,
            created_at=created_at,
            updated_at=updated_at
        )
    )
    execute_cursor(sql, values, connection)


def update_oep_customer(customer, connection):
    print(f"Updating OEP customer for email: {customer.email}")
    updated_at = datetime.utcnow()
    sql = """
        UPDATE customers
        SET go1_active = %(go1_active)s, updated_at = %(updated_at)s
        WHERE email = %(email)s
    """
    values = (
        dict(go1_active=customer.go1_active, updated_at=updated_at, email=customer.email)
    )
    execute_cursor(sql, values, connection)
