# ReferralCrimeMap
 I accessed and analyzed multiple datasets (LAPD crime data, Dep. of Child and Families Services referral data, LA walk score, LA city zip codes, LA population) to see if community atmosphere is relevant to child maltreatment. For community atmosphere, LAPD crime reports and walk score data were used. For child maltreatment, DCFS child referral records were used. This project analyzed those data in LA city in 2016 at a zip code level. In this project, I used python language to get data through API and web-scraping, then stored them in a database using SQL. I merged the datasets to analyze. I mapped the frequency of maltreatment data and crime reports at a zip code level on the map of LA city. I also created charts and graphs to show the results.
 
 ![alt text](https://github.com/eunieunz/ReferralCrimeMap/blob/master/output/UML_diagram.png?raw=true)

 
1. How to run the code

Type the code below:
pythonw AHN_EUNHYE_hw6.py -source=remote

- You can choose remote or local source by '-source=remote' or '-source=local'.
- Please use pythonw instead of python if you run this code on OSX
- When AHN_EUNHYE_hw5.py is invoked, it imports modules, parses the argument, and load datasets via API or web scraping. It models the data and analyses.
- It produces charts and maps. Maps are saved in the same directory.

2. Any major 'gotchas' to the code?

- It could be improved by making it go through datasets it already has, and download datasets that are missing. Also, it takes a while to download crime referral as it has over 200k rows. 

3. Anything else you feel is relevant to the grading

- This program accesses 5 data sources (LAPD crime data, DCFS referral data, LA walk score, LA city zip codes, LA population) and two datafiles, 'Crime2016_zip.csv', 'zip-code-tabulation-areas-2012.geojson'. I have already discussed with Jeremy about this and this is due to geocoding. Required datasets are all included in the folder. 
- You will see some graph pop-ups as you run this code. Also, a couple of maps will be saved in the same directory. 

4. What did you set out to study?

- This project is to see if community atmosphere is relevant to child maltreatment. For community atmosphere, LAPD crime reports and walk score data were used. For child maltreatment, DCFS child referral records were used. This project analyses those data in LA city in 2016 at a zip code level.
- I specifically looked at domestic violence crime report, which was coded as 'INTIMATE PARTNER ASSAULT' in LAPD crime report data. I coded it as domestic violence (DV), but did not include any crime report related to child ('CHILD NEGLECT', 'CHILD PHYSICAL ABUSE', etc.). 
- My questions were a) are regional crime report rates related to child maltreatment reports (DCFS referrals)?, b) is walk score in each zip code related to child maltreatment referrals?, and c)are domestic violence crime report rates related to child maltreatment referrals?

5. What did you discover? What was your conclusions?

- In terms of crime reports in LA city, some k-town area (90010, 90021) and some part in DTLA (90014) are shown to experience the highest crime reports per capita. (Please see the map, 'c_count_map.html', in the folder.)
- In terms of the proportion of intimate partner crime (mean = 5.8%), Long Beach (90813) (20%), South Pasadena (91030) (17.6%), and Inglewood (90302) (17.4%) are top three zip codes where show the highest proportion of domestic violence in crime reports.
- It was found that over 60% of children referred to DCFS in LA city are Hispanic children and 18% of them are Black. While 60% of the referrals have 5 day investigation response, over 20% of them required immediate investigation responses. 4.3% of the children referred were removed from their home after investigation. (Please see the map, 'r_count_map.html')
- The average referral rate per capita at a zip code level was 1.5%. It was found that South LA (Vernon (90058) (5.8%), area around Avalon Gardens (90003) (5.4%), West Athens (90044) (4.8%)) had the highest child maltreatment referral rate per capita in 2016. (Please see the map, 'ref_rate_map.html')
- The major finding of this project was that there was a significant positive correlation between the proportion of domestic violence crime and DCFS referral rate (r=0.66, p<0.001). It is also shown by the last graph.

6. What difficulties did you have in completing the project?

- This is my first 'real' programming other than jupyter notebook. It took me long time to debug. Figuring out how to do mapping without getting too complicated was also challenging. But in general, I had so much fun!

7. What skills did you wish you had while you were doing the project?

- Mapping skill would have been helpful. I wish I could have done better in manipulating dataframe with pandas and numpy.

8. What would you do 'next' to expand or augment the project?

- It would be interesting if I could add more community culture variables, such as libraries, community centres, and schools, to see if having these infrastructure affects child maltreatment referrals. Unemployment, average family size, or crimes involved weapon are somehow related to child maltreatment would be also interesting.



