import pandas as pd
import pandas.io.sql as pd_sql
from sodapy import Socrata
import requests 
import sqlite3 as sq 
from bs4 import BeautifulSoup


class ClassReferral:
    def __init__(self, arg=None):
        if arg == "remote":
            print ("Remote source selected.")
        elif arg == "local":
            print("Local source selected.")
        else:
            print("Wrong or no arg. Please select 'local' or 'remote' source")
            exit()

        self.storage = arg
    # Getting DCFS referral data
    def getData(self):
        if self.storage == "remote":
            print("Getting DCFS referral data from remote source.")

            # API request
            client_dcfs = Socrata('data.lacounty.gov','7pTgt6f2oTY53aDI1jXNJoNZD')
            offset_temp = 0
            dcfs_df=pd.DataFrame()

            conn = sq.connect("ReferralCrimeMap.db")
            cur = conn.cursor()
            cur.execute('DROP TABLE IF EXISTS dcfs')

            print('Inserting DCFS referral dataframe into ReferralCrimeMap.db.')
            while True:
                results = client_dcfs.get("8vmx-hhtu", limit=5000, offset=offset_temp)
                dcfs_df = pd.DataFrame.from_records(results)
                # Break the loop and stop requesting if the block is empty 
                if dcfs_df.empty == True:
                    break
                # Insert dataframe into ReferralCrimeMap.db
                dcfs_df['location'] = dcfs_df['location'].astype('str')
                pd_sql.to_sql(dcfs_df, 'dcfs', conn, if_exists='append', index=False)
                
                offset_temp+=5000
                # I didn't use time.sleep as this API is unlimited
                # time.sleep(1)
            conn.close()

        else:
            print ("Getting DCFS referral data from local source.")
            conn = sq.connect("ReferralCrimeMap.db")
            cur = conn.cursor()
            query = '''
                    SELECT *
                    FROM dcfs
                    '''
            try:
                dcfs = pd.read_sql(query, conn)
                conn.close()
                print(dcfs.head())
            # If the table does not exist it will throw an error.
            except Exception as e:
                print('There is an error:', e)
                print('Please enter remote source.')
                exit()
                



            

            

    
