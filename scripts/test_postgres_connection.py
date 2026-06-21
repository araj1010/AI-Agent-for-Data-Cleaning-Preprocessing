import psycopg2

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "test1234"
# DB_URL = "postgresql://postgres:test1234@localhost:5432/postgres"

try:
    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    print("✅Connected to PostgreSQL database successfully")

    # Execute a simple query to verify the connection
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cursor.fetchall()
    print("✅ Tables in the database:")
    for table in tables:
        print(table[0])

    # Close the connection
    cursor.close()
    conn.close()
    print("✅PostgreSQL connection Closed")

except Exception as e:
    print(f"❌ Error: {e}")