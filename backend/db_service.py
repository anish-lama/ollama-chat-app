import psycopg2

def run_sql(query):

    conn = psycopg2.connect(
        host="localhost",
        database="HRSystem",
        user="postgres",
        password="9841",
        port="5432"
    )

    cursor = conn.cursor()

    cursor.execute(query)

    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    cursor.close()
    conn.close()

    return columns, rows
