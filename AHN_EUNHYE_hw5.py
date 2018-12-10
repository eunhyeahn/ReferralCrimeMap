import argparse
import classReferral
import classWalkScore
import classCrime
import cleanReferral
import classPop
import Analysis

# Assigning parser
# Select -source=remote if this is your first time running this program
parser = argparse.ArgumentParser(description='This code is wrtten for loading DCFS Referral data. Select remote if you are running this program first time.')
parser.add_argument("-source", help="Data location, 'remote' or 'local'.")
args = parser.parse_args()

if args.source == None:
    print(parser.print_help())
    exit()

# Get DCFS referral data (API)
print("\n * Getting DCFS referral data.")
dcfs = classReferral.ClassReferral(args.source)
dcfs.getData()

# Get LA City zip codes (Web scraping)
# Get Walk Score data based on LA City zip codes (Web scraping)
print("\n * Getting LA City zip copdes and walk score data")
walkScore = classWalkScore.ClassWalkScore(args.source)
walkScore.getLAcityZip()
walkScore.getData()

# Get LA population data (API)
print("\n * Getting LA population data")
pop = classPop.ClassPop(args.source)
pop.getLApop()

# Get crime report data (API)
print("\n * Getting crime records data")
crime = classCrime.ClassCrime(args.source)
crime.getData()

# Cleaning data and data modeling
print("\n * Clean data and modeling")
cleanReferral.CleanReferral()
cleanReferral.ZipCrime()

# Analyze each dataset and combined dataset
Analysis.loadGeoJSON()
Analysis.Crime_analysis()
Analysis.DCFS_analysis()
Analysis.Combine_analysis()
Analysis.Correlation_graph()
