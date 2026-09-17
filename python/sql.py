# IMPORTATION

import os

from dotenv import load_dotenv
from ratio import cagr_ca, df_ratios
from sqlalchemy import create_engine
from valorisation import df_dcf

# CONNEXION AVEC SQL

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")

with engine.connect() as connexion:
    print("Connexion PostgreSQL réussie !")

# TRANSFERT DES DF

df_ratios.to_sql("ratios_financiers",engine,if_exists="replace",index=False)

print("Transfert df_ratios terminé !")

cagr_ca.to_sql("cagr_ca",engine,if_exists="replace",index=False)

print("Transfert cagr_ca terminé !")

df_dcf.to_sql("valorisation_societes",engine,if_exists="replace",index=False)

print("Transfert df_dcf terminé !")

