# Date: October 03, 2022


import pandas as pd
import glob 
import os
import numpy as np
from numpy import int64




# Read all skater players from skaters.csv files
Skaters_path = '/Users/banafshehkhazali/Documents/CPSC672/Skaters'
all_files = glob.glob(Skaters_path + "/*.csv")

Skaterslst = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    Skaterslst.append(df)

skatersdf = pd.concat(Skaterslst, axis=0, ignore_index=True)


#Find players that played on 5-on-5 basis
situation = skatersdf[skatersdf['situation'] == '5on5']
skaters5on5 = pd.DataFrame(situation)


# Extract players Ids in order to use them for similar name/lastname
df = pd.concat([skaters5on5["name"], skaters5on5["playerId"]], axis=1)
skatersdf_5on5 = df.drop_duplicates("playerId")


# for each node find all lines they played on
# Read all lines from Lines.csv files
linePath = '/Users/banafshehkhazali/Documents/CPSC672/Lines'
line_files = glob.glob(linePath + "/*.csv")

Lineslst = []

for filename in line_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    Lineslst.append(df)

linedf = pd.concat(Lineslst, axis=0, ignore_index=True)


# Seperate lineID each player so we can replace the lastname of players with ther full name
N = 7
split_string = lambda x: pd.Series([x[i:i+N] for i in range(0, len(x), N)])
new_var = linedf['lineId'].apply(split_string).fillna('')
new_var.columns = 'playerId' + (new_var.columns + 1).astype(str).str.zfill(1)
linedf = linedf.join(new_var)
linesdf = linedf.copy( deep = True)

# Replace the lastname of players with ther full name
linesdf.rename(columns = {'playerId1':'playerId'}, inplace = True)
linesdf['playerId'] = linesdf['playerId'].astype(int64)
merged_df = linesdf.merge(skatersdf_5on5, how='left', on='playerId')
merged_df = linesdf.merge(skatersdf_5on5, how='left', on='playerId')
linesdf.rename(columns = {'playerId':'playerId1'}, inplace = True)
linesdf.rename(columns = {'playerId2':'playerId'}, inplace = True)
merged_df['playername1']=merged_df['name_y']
linesdf['playerId'] = linesdf['playerId'].astype(int64)
merged_df2 = linesdf.merge(skatersdf_5on5, how='left', on='playerId')

merged_df2['playername2']=merged_df2['name_y']
merged_df2['playername1']=merged_df['playername1']
linesdf.rename(columns = {'playerId':'playerId2'}, inplace = True)
linesdf.rename(columns = {'playerId3':'playerId'}, inplace = True)
linesdf[linesdf['playerId']==''] = '0'
linesdf['playerId'] = linesdf['playerId'].astype(int64)
merged_df3 = linesdf.merge(skatersdf_5on5, how='left', on='playerId')
merged_df3['playername3']=merged_df3['name_y']
merged_df3['playername1']=merged_df['playername1']
merged_df3['playername2']=merged_df2['playername2']
final_Lines_df = merged_df3.copy()
final_Lines_df['player names']=final_Lines_df.apply(lambda x:'%s-%s-%s' % (x['playername1'],x['playername2'],x['playername3']),axis=1)
# print(final_Lines_df)

# Save new data in a csv file
final_Lines_df.to_csv('/Users/banafshehkhazali/Documents/CPSC672/Lines.csv')