import os
import psycopg2
from psycopg2 import pool, DatabaseError
from dotenv import load_dotenv

load_dotenv()

# Global variable to hold the pool
_connection_pool = None

def init_pool():
    """Initializes the pool once when the app starts."""
    global _connection_pool
    try:
        if _connection_pool is None:
            _connection_pool = psycopg2.pool.SimpleConnectionPool(
                1,      # Minimum connections to keep open
                10,     # Maximum connections to allow
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            print("Connection pool initialized.")
    except Exception as e:
        print(f"Error initializing pool: {e}")

def execute_query(query, params=None, is_select=False):
    """Borrows a connection from the pool, runs the query, and returns it."""
    if _connection_pool is None:
        init_pool()
        
    conn = None
    try:
        # 1. Borrow a connection from the pool
        conn = _connection_pool.getconn()
        cur = conn.cursor()
        
        cur.execute(query, params)
        
        if is_select:
            result = cur.fetchall()
            # 2. Return connection BEFORE returning the result
            _connection_pool.putconn(conn)
            return result
        
        conn.commit()
        # 2. Return connection to pool
        _connection_pool.putconn(conn)
    except DatabaseError as e:
        print(f"SQL Error: {e}")
        if conn:
            conn.rollback()
            _connection_pool.putconn(conn)
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            _connection_pool.putconn(conn)
    return None

def close_all_connections():
    """Call this when the GUI window is closed to shut down the pool."""
    if _connection_pool:
        _connection_pool.closeall()
        print("All database connections closed.")

def get_direct_connection():
    """Returns a direct database connection using environment variables."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Exception as e:
        print(f"Error creating direct connection: {e}")
        return None