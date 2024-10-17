import bcrypt
import pandas as pd
import os
import psycopg
from sqlalchemy import create_engine
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.dialects.postgresql import ARRAY

password_psql = os.getenv('password_db')
'''conn = psycopg.connect(
    dbname="db_dora",
    user="cromex",
    password="Lucyzesky*6",
    host="35.180.30.181",
    port="5432"
)'''


username = 'cromex'
password = password_psql
host = '35.180.30.181'
port = '5432'
database = 'db_dora'


database_url = f'postgresql+psycopg://{username}:{password}@{host}:{port}/{database}'

# Créer l'engine SQLAlchemy
engine = create_engine(database_url)

def envoi_df_dans_DBB(df,dict_config_col_BDD_DORA_vierge):
    # Exemple de requête
    def generation_dict_dtypes(dict_config_col_BDD_DORA_vierge):
        dict_dtypes={}
        for nom_col,type_col in dict_config_col_BDD_DORA_vierge['type_col_SQL'].items():
            nom_col = nom_col.lower()
            if type_col=="PRIMARY KEY":
                dict_dtypes[nom_col]=String
            if type_col=="VARCHAR(255)":
                dict_dtypes[nom_col]=String
            if type_col=="TEXT[]":
                dict_dtypes[nom_col]=ARRAY(String)
            if type_col=="INTEGER":
                dict_dtypes[nom_col]=Integer 
            if type_col=="BOOLEAN":
                dict_dtypes[nom_col]=Boolean
        return dict_dtypes
    dict_dtypes = generation_dict_dtypes(dict_config_col_BDD_DORA_vierge)
    df.to_sql('bdd_dora_sql_paot', engine, if_exists='replace', index=False,    dtype=dict_dtypes)
    return df





