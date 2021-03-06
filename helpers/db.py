import psycopg2

DB_SETTINGS = {
    "host": "localhost",
    "user": "docker",
    "password": "password",
    "database": "meeting-room-remover",
    "port": 5432
}


def get_connection():
    return psycopg2.connect(**DB_SETTINGS)


def get_cursor(cursor_class=None):
    c = get_connection()

    if cursor_class:
        cursor = c.cursor(cursor_factory=cursor_class)
    else:
        cursor = c.cursor()

    return c, cursor


def get_from_db(query, parameters=None, cursor_class=None):
    if cursor_class:
        c, cursor = get_cursor(cursor_class=cursor_class)
    else:
        c, cursor = get_cursor()

    if isinstance(parameters, tuple):
        cursor.execute(query, parameters)
    else:
        cursor.execute(query)

    result = cursor.fetchall()
    c.rollback()
    cursor.close()
    c.close()

    return result
