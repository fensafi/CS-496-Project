import psycopg2

def connect_db():
    return psycopg2.connect(
        dbname="wku_cs_advising",
        user="postgres",
        password="root",
        host="localhost",  # or your remote host
        port="5432"
    )

def fetch_faq():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT question, answer FROM faq")
    faq_list = cur.fetchall()
    cur.close()
    conn.close()
    return faq_list

def fetch_courses():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT course_code, course_name, description FROM courses")
    courses = cur.fetchall()
    cur.close()
    conn.close()
    return courses

def fetch_prerequisites():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT course_code, prerequisite_code FROM prerequisites")
    prereqs = cur.fetchall()
    cur.close()
    conn.close()
    return prereqs