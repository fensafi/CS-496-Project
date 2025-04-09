
import psycopg2
import pandas as pd

# PostgreSQL connection details
DB_NAME = "wku_cs_advising"
DB_USER = "postgres"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = "5432"

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cur = conn.cursor()

# Load CSV files
courses_df = pd.read_csv("courses.csv")
prereqs_df = pd.read_csv("prerequisites.csv")

# Upload courses data
for _, row in courses_df.iterrows():
    cur.execute(
        "INSERT INTO courses (course_code, course_name, credits, description) VALUES (%s, %s, %s, %s) ON CONFLICT (course_code) DO NOTHING",
        (row['course_code'], row['course_name'], row['credits'], row['description'])
    )

# Upload prerequisites data
for _, row in prereqs_df.iterrows():
    cur.execute(
        "INSERT INTO prerequisites (course_code, prerequisite_code) VALUES (%s, %s)",
        (row['course_code'], row['prerequisite_code'])
    )

conn.commit()
cur.close()
conn.close()

print("✅ Courses and prerequisites uploaded to PostgreSQL!")
