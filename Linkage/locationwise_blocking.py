import pandas as pd
import sys

LOCATION_TYPE = 'city'

if len(sys.argv) > 1:

    LOCATION_TYPE = sys.argv[1]

print(LOCATION_TYPE)

LINKAGE_DSB = r'D:\Data\Linkage\FL\FL18\linkage\voterside.csv'
LOC_VOTERS_PATH = r'D:\Data\Linkage\FL\FL18\linkage\{}wise\voterside_{}.csv'

df_voter = pd.read_csv(LINKAGE_DSB, header=0)

locations = df_voter[LOCATION_TYPE].unique()

print(len(locations))

for loc in locations:

    if type(loc) == str and loc.isalnum():

        df_loc_voters = df_voter.loc[df_voter[LOCATION_TYPE] == loc]

        df_loc_voters.to_csv(LOC_VOTERS_PATH.format(LOCATION_TYPE, loc), index=False)

        pass

    else:

        print(loc)
