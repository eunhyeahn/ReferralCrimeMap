import pandas as pd
import pandas.io.sql as pd_sql
import sqlite3 as sq

def CleanReferral():
    print("Joining referral data to LA City zip codes to filter referrals within LA City.")
    # Join DCFS and LA City zip code by zip code
    # To obtain referrals made within LA City (DCFS referral data is originally county-level)
    conn = sq.connect('ReferralCrimeMap.db')
    cur = conn.cursor()
    query = '''
            SELECT *
            FROM dcfs
            JOIN LAzip
            ON dcfs.ref_zip = LAzip.zipcode
            '''
    dcfs_all = pd.read_sql(query,conn)
    conn.close()

    # Select the referrals received in the focal year 2016
    print("Select the referrals received in focal year 2016.")
    dcfs_all['ref_year'] = dcfs_all['ref_date'].map(lambda x: x.split('-')[0])
    dcfs_all['ref_month'] = dcfs_all['ref_date'].map(lambda x: x.split('-')[1])
    dcfs_all.rename(columns={'prime_key':'zip_ID'}, inplace=True)
    dcfs16 = dcfs_all[dcfs_all['ref_year']=='2016']
    
    # Save the data into ReferralCrimeMap.db
    print("Referral_LAcity2016 is saved to ReferralCrimeMap.db")
    conn = sq.connect('ReferralCrimeMap.db')
    pd_sql.to_sql(dcfs16, 'Referral_LAcity2016', conn, if_exists='replace',index=False)
    conn.close()
    
def ZipCrime():
    # Since converting the coordinates into zip codes takes 2.5 hours,
    # Crime2016_zip.csv is submitted with this code (the conversion codes are below.)
    # Loading Crime2016_zip instead of converting the coordinates into zip code.
    print("Loading Crime2016_zip.csv")
    crime_zip = pd.read_csv('Crime2016_zip.csv')
    crime_zip = crime_zip.drop(crime_zip.columns[0], axis=1)
    conn = sq.connect("ReferralCrimeMap.db")
    pd_sql.to_sql(crime_zip, 'Crime2016_zip', conn, if_exists='replace', index=False)

    # Join with LA City zip codes to filter cases happened within LA City
    print("Joining with LAzip to filter within LA City crime reports.")
    query = '''
            SELECT *
            FROM Crime2016_zip
            JOIN LAzip
            ON Crime2016_zip.zips = LAzip.zipcode
            '''
    crime2016_zip = pd.read_sql(query,conn)
    crime2016_zip.rename(columns={'prime_key':'zip_ID'}, inplace=True)
    print("Dataframe is saved to ReferralCrimeMap.db")
    pd_sql.to_sql(crime2016_zip, 'Crime2016_zip', conn, if_exists='replace', index=False)
    conn.close()
    
# Below is to get zip codes by using uszipcode module.
# This convers the coordinates into zip codes and add them to the table in a new column 'zipcode'.
# However, This takes over 2 hours, since there are 220k rows.
# Thus, 'Crime2016_zip.csv' is attached to my assignment zip file.

##    from uszipcode import Zipcode
##    from uszipcode import SearchEngine
##    
##    conn = sq.connect("ReferralCrimeMap.db")
##    query = '''
##            SELECT date_rptd, month_rptd, crm_cd, crm_cd_desc, weapon_used_cd, count, lat, long
##            FROM Crime2016
##            '''
##    try:
##        cdf = pd.read_sql(query,conn)
##        conn.close()
##    except Exception as e:
##        print(e)
##        exit()
##
##    cdf['zipcode'] = None
##    zip_list = list()
##    for i in range(len(cdf)):
##        try:
##            lat = float(cdf.iloc[i,6])
##            long = float(cdf.iloc[i,7])
##            search = SearchEngine(simple_zipcode=True)
##            result = search.by_coordinates(lat,long,radius=30, returns=1)
##            cdf.iloc[i,8]=result[0].zipcode
##        except Exception as e:
##            print(e)
##            cdf.iloc[i,8]=None
##            continue
##    cdf.to_csv('Crime2016_zip.csv')
##            
    
