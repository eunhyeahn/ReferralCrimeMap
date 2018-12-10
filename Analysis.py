import folium
import pandas as pd
import pandas.io.sql as pd_sql
import sqlite3 as sq 
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns

def loadGeoJSON():
    with open('zip-code-tabulation-areas-2012.geojson', 'r') as jsonFile:
        data = json.load(jsonFile)
    tmp = data

    # remove ZIP codes not in our dataset
    conn = sq.connect('ReferralCrimeMap.db')
    cur = conn.cursor()
    LAzip = pd.read_sql('SELECT * FROM LAzip', conn)
    conn.close
    geozips = []
    for i in range(len(tmp['features'])):
        if tmp['features'][i]['properties']['name'] in list(LAzip['zipcode']):
            geozips.append(tmp['features'][i])

    # creating new JSON object
    njson = dict.fromkeys(['type', 'features'])
    njson['type']='FeatureCollection'
    njson['features']=geozips

    # save JSON
    open("updated.json", "w").write(
        json.dumps(njson, sort_keys=True, indent=4, separators=(',',': '))
    )

def Create_map(table, zips, mapped_feature, add_text=''):
    # Reading GeoJSON file
    la_geo = r'updated.json'
    
    # initiate a Folium map
    m = folium.Map(location = [34.0522, -118.2437], zoom_start = 11)
    
    # creating a choropleth map
    m.choropleth(
    geo_data = la_geo,
    fill_opacity = 0.7,
    line_opacity = 0.2,
    data = table,
    key_on = 'feature.properties.name',
    columns = [zips, mapped_feature],
    fill_color = 'RdYlGn_r',
    legend_name = add_text
    )
    folium.LayerControl().add_to(m)
    
    # save map
    m.save(outfile = mapped_feature + '_map.html')



def Crime_analysis():
    print("\n ************************\n * Crime data analysis * \n ************************")
    # load crime data joined with population variable
    query = '''
            SELECT Crime2016_zip.month_rptd, Crime2016_zip.crm_cd, Crime2016_zip.crm_cd_desc, Crime2016_zip.count, 
                   Crime2016_zip.lat, Crime2016_zip.long, Crime2016_zip.zipcode, Population.total_population
            FROM Crime2016_zip
            JOIN Population
            ON Population.zip_code = Crime2016_zip.zipcode
            '''
    conn = sq.connect('ReferralCrimeMap.db')
    crime = pd.read_sql(query, conn)

    # create binary DV(domestic violence) var by filtering 'INTIMATE PARTNER' in crime code
    crime['inti_part'] = crime['crm_cd_desc'].str.contains(r'INTIMATE PARTNER')
    crime['inti_part']=crime['inti_part'].replace([True,False],[1,0])
    # rename count as c_count
    crime = crime.rename(columns={'count':'c_count'})
    #change data type
    crime['total_population'] = crime['total_population'].astype(int)
    # delete rows that have lower than 20 people in a zip code
    crime= crime[(crime['total_population'] >=20)]

    # monthly crime report
    crime_month = crime['c_count'].groupby(crime['month_rptd']).sum()
    print(" * Number of crime reports in each month in 2016")
    print(crime_month.head(12))

    # group data by zipcode
    crime_zip = crime.groupby(['zipcode']).agg({'c_count':'sum','inti_part':'sum',
                                                'total_population':'mean'})    
    # crime rate, domestic violence(DV) rate 
    crime_zip['crime_rate'] = crime_zip['c_count']/crime_zip['total_population']*100
    crime_zip['DV_rate'] = crime_zip['inti_part']/crime_zip['c_count']*100
    crime_zip.reset_index(level=0, inplace=True)
    # save to ReferralCrimeMap.db
    conn = sq.connect('ReferralCrimeMap.db')
    pd_sql.to_sql(crime_zip, 'Grouped_crime', conn, if_exists='replace', index=False)

    DV_rate = crime_zip.sort_values(by=['DV_rate'], ascending=False)
    crime_rate = crime_zip.sort_values(by=['crime_rate'], ascending=False)
    print("\n * 10 zip codes that have the highest crime rate")
    print(crime_rate.iloc[:,[0,4]].head(10))
    print("\n * 10 zip codes that have the highest intimate partner crime rate")
    print(DV_rate.iloc[:,[0,5]].head(10))

    # drawing maps, c_count_map.html
    print("'\n * Number of crime reports in each zip code map' (c_count_map.html) is saved in the directory.")
    Create_map(crime_zip, 'zipcode', 'c_count', 'Number of crime reports')

def DCFS_analysis():
    print("\n ************************\n * DCFS data analysis * \n ************************")
    # load DCFS file joined with population data
    query = '''
        SELECT Referral_LAcity2016.age_range, Referral_LAcity2016.removal_ind, Referral_LAcity2016.ethnicity, 
        Referral_LAcity2016.count, Referral_LAcity2016.gender, Referral_LAcity2016.referral_response_desc,
        Referral_LAcity2016.zipcode, Population.total_population
        FROM Referral_LAcity2016
        JOIN Population
        ON Population.zip_code = Referral_LAcity2016.zipcode'''
    conn = sq.connect("ReferralCrimeMap.db")
    dcfs = pd.read_sql(query, conn)
    print("\n * DCFS data")
    print(dcfs.head())

    # recode variables
    print("\n ... Recoding variables...")
    dcfs['age']=dcfs['age_range'].map({'  Birth - 2 years':'<5 years old', ' 3 - 4 years':'<5 years old',
                                      ' 5 - 9 years':'5-13 years old','10 - 13 years':'5-13 years old',
                                      '14 - 15 years':'14-17 years old','16 - 17 years':'14-17 years old',
                                      '18 and Over':'18 and Over'})

    dcfs['total_population'] = dcfs['total_population'].astype(int)
    dcfs = dcfs.rename(columns={'count':'r_count'})
    dcfs['r_count']=dcfs['r_count'].astype(int)

    # make catetorical vars as categorical types
    dcfs['ethnicity']=dcfs['ethnicity'].astype('category')
    dcfs['ethnicity'].cat.set_categories(['White', 'Other', 'Hispanic', 'Black', 'Asian/Pacific Islander',
           'American Indian/Alaskan Native'],inplace=True)

    dcfs['gender']=dcfs['gender'].astype('category')
    dcfs['gender'].cat.set_categories(['Male', 'Female', 'Unknown'], inplace=True)

    dcfs['referral_response_desc']=dcfs['referral_response_desc'].astype('category')
    dcfs['referral_response_desc'].cat.set_categories(['5 Day', 'Immediate', '3 Day', '10 Day', 'Evaluate Out',
           'N/A Secondary Report'], inplace=True)

    dcfs['age']=dcfs['age'].astype('category')
    dcfs['age'].cat.set_categories(['<5 years old','5-13 years old', '14-17 years old', '18 and Over'], inplace=True)

    # demographics
    print("\n * Demographic information of referred children in 2016")
    dcfs_age = dcfs.groupby(['age']).agg({'r_count':'sum'})
    dcfs_age['rate'] = dcfs_age['r_count']/len(dcfs)*100
    print("\n * Referred chileren's age")
    print(dcfs_age.rate.head())
    dcfs_age['rate'].plot(kind='bar', title="Referred children's age")
    plt.show()

    dcfs_gen = dcfs.groupby(['gender']).agg({'r_count':'sum'})
    dcfs_gen['rate'] = dcfs_gen['r_count']/len(dcfs)*100
    print("\n * Children's gender")
    print(dcfs_gen.rate.head())

    dcfs_eth = dcfs.groupby(['ethnicity']).agg({'r_count':'sum'})
    dcfs_eth['rate']=dcfs_eth['r_count']/len(dcfs)*100
    dcfs_eth['rate'].plot(kind='bar', title="Referred children's ethnicity")
    plt.show()
    print("\n * Children's ethnicity")
    print(dcfs_eth.rate.head(6))

    dcfs_res = dcfs.groupby(['referral_response_desc']).agg({'r_count':'sum'})
    dcfs_res['rate'] = dcfs_res['r_count']/len(dcfs)*100
    print("\n * DCFS response type")
    print(dcfs_res.rate.head(6))

    dcfs_remov = dcfs.groupby(['removal_ind']).agg({'r_count':'sum'})
    dcfs_remov['rate'] = dcfs_remov['r_count']/len(dcfs)*100
    print("\n * Children removed from home")
    print(dcfs_remov.rate.head())

    # group by zip code
    print("\n * Data grouped by zip code")
    dcfs_zip = dcfs.groupby(['zipcode']).agg({'r_count':'sum', 'total_population':'mean'})
    dcfs_zip['ref_rate'] = dcfs_zip['r_count']/dcfs_zip['total_population']*100
    dcfs_zip.reset_index(level=0, inplace=True)
    print(dcfs_zip.head())

    # save data into the database
    conn = sq.connect("ReferralCrimeMap.db")
    pd_sql.to_sql(dcfs_zip, 'Grouped_dcfs', conn, if_exists='replace', index=False)
    conn.close()

    # zip codes that have the highest referrals
    ref = dcfs_zip.sort_values(by=['ref_rate'], ascending=False)
    print("\n * 10 zip codes that have the highest referral rate (referrals/population)")
    print(ref.iloc[:,[0,3]].head(10))
    
    # mapping - saved in the directory
    print("'Number of DCFS referrals in each zip code map' (r_count_map.html) is saved in the directory.")
    Create_map(dcfs_zip, 'zipcode', 'r_count', 'Number of DCFS referrals')
    print("'Number of DCFS referral rates per population in each zip code map' (ref_rate_map.html) is saved in the directory.")
    Create_map(dcfs_zip, 'zipcode', 'ref_rate', 'Percentage of DCFS referrals')

def Combine_analysis():
    print("\n ***************************\n * Combined data analysis * \n ***************************")
    print("\n Combine crime data, DCFS data, and walk score data together by joining on zip code.")
    # join and load three datasets
    query = '''
            SELECT Grouped_crime.zipcode, Grouped_crime.c_count, Grouped_crime.inti_part, Grouped_crime.total_population,
                    Grouped_crime.crime_rate, Grouped_crime.DV_rate,
                    Grouped_dcfs.r_count, Grouped_dcfs.ref_rate, WalkScore.walk_score
            FROM Grouped_crime
            JOIN Grouped_dcfs
            ON Grouped_crime.zipcode = Grouped_dcfs.zipcode
            JOIN WalkScore
            ON Grouped_dcfs.zipcode = WalkScore.zip_code'''
    conn = sq.connect('ReferralCrimeMap.db')
    comb = pd.read_sql(query, conn)

    # save the joined dataset into the db
    pd_sql.to_sql(comb, 'Combined', conn, if_exists='replace', index=False)

    print("\n * Combined dataset")
    print(comb.columns)
    print(comb.head())

    comb.walk_score = comb.walk_score.astype(int)

    # Correlation coefficient
    corr = np.corrcoef([comb.crime_rate, comb.DV_rate, comb.ref_rate, comb.walk_score])
    print("\n * Correlation Coefficient between key variables")
    list2 = ['crime_rate', 'DV_rate', 'ref_rate', 'walk_score']
    print(list2)
    print(corr)

    # Pearson's r
    # Test all possible pairs of the key vars and report only those significant (p<0.05)
    print("\n * Pearson r ")
    list = [comb.crime_rate, comb.DV_rate, comb.ref_rate, comb.walk_score]
    for i in range(len(list)):
        if i <1:
            (cc,p) = stats.pearsonr(list[i],list[i+3])
            if p < 0.05:
                print(list2[i], "and", list2[i+3],"are significantly correlated.")
                print("r = %.2f and p = %.3f" % (cc,p))
            else:
                pass
        if i < 3:
            (cc, p) = stats.pearsonr(list[i],list[i+1])
            if p < 0.05:
                print(list2[i], "and", list2[i+1],"are significantly correlated.")
                print("r = %.2f and p = %.3f" % (cc,p))
            else:
                pass
        if i < 2:
            (cc, p) = stats.pearsonr(list[i],list[i+2])
            if p < 0.05:
                print(list2[i], "and", list2[i+2],"are significantly correlated.")
                print("r = %.2f and p = %.3f" % (cc,p))
            else:
                pass
        else:
            pass

def Correlation_graph():
    # load the file
    conn = sq.connect("ReferralCrimeMap.db")
    comb = pd.read_sql('SELECT * FROM Combined', conn)
    print("\n * Relationship between the number of domestic violence reports and DCFS referrals.")
    sns.set_style("darkgrid")
    sns.lmplot(x='DV_rate', y ='ref_rate', data = comb, height=7)
    plt.gca().set_title('Relationship between the number of domestic violence reports and DCFS referrals.')
    plt.show()
        
            
        
        

