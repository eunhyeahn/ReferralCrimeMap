import pandas as pd
import pandas.io.sql as pd_sql
from sodapy import Socrata
import requests 
import sqlite3 as sq 
from bs4 import BeautifulSoup
import json

class ClassPop:
    def __init__(self, arg=None):
        if arg == "remote":
            print("Remote source selected.")
        elif arg == "local":
            print("Local source selected.")
        else:
            print("Wrong or no arg. Please select 'local' or 'remote'.")
            exit()
        self.storage = arg

    def getLApop(self):
        # Getting remote data
        if self.storage == "remote":
            print(" * Getting LA population data from remote source.")

            # Get LA population data
            client_pop = Socrata('data.lacity.org', '7pTgt6f2oTY53aDI1jXNJoNZD')
            results = client_pop.get('a6pt-xt54', limit=500)
            # Save the data as df
            pop = pd.DataFrame.from_records(results)
            # Save the df into db
            conn = sq.connect("ReferralCrimeMap.db")
            pd_sql.to_sql(pop, 'Population', conn, if_exists='replace', index=False)
        # Getting local data
        else:
            print(" * Getting population data from local source.")

            conn = sq.connect("ReferralCrimeMap.db")
            cur = conn.cursor()
            query='SELECT * FROM Population'
            try:
                pop = pd.read_sql(query, conn)
                conn.close()
                print(pop.head())
            except Exception as e:
                print("There is an error:", e)
                print("Please enter correct data source.")
                exit()

