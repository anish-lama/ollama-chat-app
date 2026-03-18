import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()  # MUST be before getenv

def run_sql(query):

    conn = psycopg2.connect(
        host = os.getenv("DB_HOST"),
        database = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        port = os.getenv("DB_PORT", "5432")
    )

    cursor = conn.cursor()

    cursor.execute(query)

    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    cursor.close()
    conn.close()

    return columns, rows
