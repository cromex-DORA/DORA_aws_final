import bcrypt
import pandas as pd
import os
import psycopg


password_psql = os.getenv('password_db')
conn = psycopg.connect(
    dbname="dora_db",
    user="ubuntu",
    password="allosome",
    host="35.180.138.1",
    port="5432"
)


def import_dict_users():
    # Exemple de requête
    query = ("SELECT * FROM db_users")
    sql_df = pd.read_sql(query, conn)
    conn.close()
    dict_users = sql_df.set_index('email').to_dict(orient='index')
    return dict_users





