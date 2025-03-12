import psycopg2

try:
    connection = psycopg2.connect(
        dbname="wku_cs_advising",
        user="super_user",
        password="super_pass",
        host="localhost",
        port="5432"
    )
    print("Connection successful")
except Exception as error:
    print(f"Error: {error}")
finally:
    if connection:
        connection.close()