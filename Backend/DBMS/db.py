
import psycopg

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "floodsense_db",
    "user": "postgres",
    "password": "TR.Bangaon1"
}

def get_connection():
    return psycopg.connect(**DB_CONFIG)

if __name__ == "__main__":
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database();")
                print("Connected successfully!")
                print("Database:", cur.fetchone()[0])
    except Exception as e:
        print("Database connection failed:")
        print(e)