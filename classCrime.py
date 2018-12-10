import pandas as pd
import pandas.io.sql as pd_sql
from sodapy import Socrata
import requests 
import sqlite3 as sq 
from bs4 import BeautifulSoup
import json

class ClassCrime:
    def __init__(self, arg=None):
        if arg == "remote":
            print("Remote source selected.")
        elif arg == "local":
            print("Local source selected.")
        else:
            print("Wrong or no arg. Please select 'local' or 'remote.")
            exit()
        self.storage = arg

    def getData(self):
        # Get crime records via API
        if self.storage == "remote":
            print("Getting crime data from remote source.\nThis takes a while (approx. 5 mins)! Please be patient.")

            # API request information
            client_crime = Socrata('data.lacity.org','7pTgt6f2oTY53aDI1jXNJoNZD')
            offset_temp = 0
            conn = sq.connect("ReferralCrimeMap.db")
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS 'Crime2016'")

            # Getting data in dataframe then manipulate before storing in ReferralCrimeMap.db
            while True:
                results = client_crime.get("7fvc-faax", limit=10000, offset=offset_temp)
                crime_df_temp = pd.DataFrame.from_records(results)
                # This loop stops when the next block of dataframe is empty
                if crime_df_temp.empty == True:
                    break

                # Split location_1 into lat and long
                # Create 'year_rptd' to filter cases reported in 2016
                # Create 'count' for later data analysis
                crime_df_temp['location_1'] = crime_df_temp['location_1'].astype('str')
                crime_df_temp['long'] = crime_df_temp['location_1'].map(lambda x: x.split(']')[0].split('[')[-1].split(',')[0])
                crime_df_temp['lat'] = crime_df_temp['location_1'].map(lambda x: x.split(']')[0].split('[')[-1].split(',')[-1])
                crime_df_temp['year_rptd'] = crime_df_temp['date_rptd'].map(lambda x: x.split('-')[0])
                crime_df_temp['month_rptd'] = crime_df_temp['date_rptd'].map(lambda x: x.split('-')[1])
                crime_df_temp['count'] = 1
                crime_df_temp = crime_df_temp[crime_df_temp['year_rptd']=='2016']
                crime_df = crime_df_temp[['date_rptd', 'month_rptd', 'crm_cd',
                                                       'crm_cd_desc', 'weapon_used_cd', 'count', 'lat', 'long']]

                # Insert dataframe into ReferralCrimeMap.db
                pd_sql.to_sql(crime_df, 'Crime2016', conn, if_exists='append', index=False)
                offset_temp+=10000

                # Shows the percentage of data 
                if offset_temp % 100000 == 0:
                    print(offset_temp/2000000*100,"%")
                else:
                    continue
            cur.execute("SELECT * FROM Crime2016")
            print(cur.fetchone())
            conn.close()

        # Load local data if -source is set to local
        else:
            print("Getting crime data from local source.")
            conn = sq.connect("ReferralCrimeMap.db")
            cur = conn.cursor()
            query = "SELECT * FROM Crime2016"
            try:
                crime = pd.read_sql(query, conn)
                conn.close()
                print(crime.head())
            except Exception as e:
                print("There is an error:", e)
                print("Please set data course as remote.")
                exit()
                  
