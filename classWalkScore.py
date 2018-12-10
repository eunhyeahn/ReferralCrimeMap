import pandas as pd
import pandas.io.sql as pd_sql
from sodapy import Socrata
import requests 
import sqlite3 as sq 
from bs4 import BeautifulSoup
import json
    
class ClassWalkScore:
    def __init__(self,arg=None):
        if arg == "remote":
            print("Remote source selected.")
        elif arg == "local":
            print("Local source selected.")
        else:
            print("Wrong or no arg. Please select 'local' or 'remote'.")
            exit()
        self.storage = arg

    def getLAcityZip(self):
        if self.storage == "remote":
            print("Getting LA City zip code from remote source.")

            # Get all zip codes in Los Angeles City (http://geohub.lacity.org/datasets/875d540d71e64b8696cc368865c2b640_0)
            url="https://opendata.arcgis.com/datasets/875d540d71e64b8696cc368865c2b640_0.geojson"
            r = requests.get(url)
            data = json.loads(r.text)
            lacity_zip = list()

            for i in range(len(data['features'])):
                try:
                    zipcode = data['features'][i]['properties']['ZIPCODE']
                    lacity_zip.append((i+1,zipcode))
                except Exception as e:
                    print(e)
                    continue
            self.lacity_zip = lacity_zip
            print("Total number of LA City zip codes:", len(lacity_zip))

            # Convert the list into dataframe
            lacity_zip_df = pd.DataFrame(lacity_zip, columns=['prime_key', 'zipcode'])

            #Insert the data frame into ReferralCrimeMap.db
            conn = sq.connect("ReferralCrimeMap.db")
            cur = conn.cursor()
            pd_sql.to_sql(lacity_zip_df, 'LAzip', conn, if_exists='replace', index=False)
            cur.execute('SELECT * FROM LAzip')
            print("Inserting LA zip codes into ReferralCrimeMab.db.")
            print(cur.fetchmany(5))
            conn.close()
        else:
            print("Getting LA City zip code from local source.")
            conn = sq.connect("ReferralCrimeMap.db")
            cur=conn.cursor()
            query = '''
                    SELECT *
                    FROM LAzip
                    '''
            try:
                lacity_zip = pd.read_sql(query, conn)
                conn.close()
                print(lacity_zip.head())
            except Exception as e:
                print("There is an error:" ,e)
                print("Please enter correct data source.")
                exit()
                

    def getData(self):
        if self.storage == "remote":
            print(" * Getting walk score data from remote source.\nThis takes a few minutes! Thanks for being patient.")

            # Get walk score
            walk_score = list()
            for i in self.lacity_zip:
                zipcode = i[1]
                zip_ID = i[0]
                url = "https://www.walkscore.com/CA/Los_Angeles/"+str(zipcode)
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'lxml')
                score = soup.find_all('div',{"style":"padding: 0; margin: 0; border: 0; outline: 0; position: absolute; top: 0; bottom: 0; left: 0; right: 0;"})
                walkScoreTag = score[0].find('img')
                walkScore = walkScoreTag.attrs['src'].split('/')[-1].split('.')[0]
                walk_score.append((zipcode,walkScore,zip_ID))

            # Convert walk score list into dataframe
            print("Convert walk score into dataframe")
            walk_score_df = pd.DataFrame(walk_score)
            walk_score_df.columns=['zip_code','walk_score','zip_ID']
            print("walk score dataframe")
            print(walk_score_df.head())

            # Insert walk score dataframe into ReferralCrimeMap.db
            print("Inserting walk score dataframe into ReferralCrimeMap.db")
            conn = sq.connect("ReferralCrimeMap.db")
            cur = conn.cursor()
            pd_sql.to_sql(walk_score_df, 'WalkScore', conn, if_exists='replace', index=False)
            cur.fetchmany(5)
            conn.close()

        else:
            print("Getting walk score from local source.")

            conn = sq.connect("ReferralCrimeMap.db")
            cur = conn.cursor()
            query = '''
                    SELECT *
                    FROM WalkScore
                    '''
            try:
                walkScore = pd.read_sql(query, conn)
                conn.close()
                print(walkScore.head())
            except Exception as e:
                print("There is an error:", e)
                print("Please enter correct data source.")
                exit()
