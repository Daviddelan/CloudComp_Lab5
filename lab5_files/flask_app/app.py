from flask import Flask
import redis
import psycopg2
import os

app = Flask(__name__)

# Redis connection
r = redis.Redis(host="redis", port=6379)

# PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL")  # Ensure DATABASE_URL is set in the environment
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Ensure table exists in PostgreSQL
cur.execute("""
    CREATE TABLE IF NOT EXISTS visits (
        id SERIAL PRIMARY KEY,
        visit_count INT NOT NULL
    );
""")
conn.commit()

# Initialize visit count in PostgreSQL if not already set
cur.execute("SELECT COUNT(*) FROM visits;")
if cur.fetchone()[0] == 0:
    cur.execute("INSERT INTO visits (visit_count) VALUES (0);")
    conn.commit()

@app.route("/")
def home():
    # Increment Redis counter
    count = r.incr("hits")

    # Update visit count in PostgreSQL
    cur.execute("UPDATE visits SET visit_count = visit_count + 1 WHERE id = 1;")
    conn.commit()

    # Fetch updated visit count from PostgreSQL
    cur.execute("SELECT visit_count FROM visits WHERE id = 1;")
    postgres_count = cur.fetchone()[0]

    return f"This page has been visited {count} times (Redis), {postgres_count} times (PostgreSQL)."


if __name__ == "__main__":
    app.run(host="0.0.0.0")

