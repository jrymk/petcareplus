import psycopg2
import os
from dotenv import load_dotenv


# global psql connection instance
psql_conn = None

def get_psql_conn():
    return psql_conn

def init_db_conn():
    load_dotenv()  # load env file info of database login
    DB_USER_NAME     = os.getenv('POSTGRES_USER')
    DB_USER_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    DB_ADDRESS       = os.getenv('POSTGRES_HOST')
    DB_PORT          = os.getenv('POSTGRES_PORT')
    DB_NAME          = os.getenv('POSTGRES_DB')
    
    global psql_conn
    psql_conn = psycopg2.connect(
        dbname = DB_NAME,
        user = DB_USER_NAME,
        host = DB_ADDRESS,
        port = DB_PORT,
        password = DB_USER_PASSWORD
    )
