# Date: October 03, 2022


import pandas as pd
import glob
import os
import numpy as np
from numpy import int64


# Read all skater players from skaters.csv files
dirname = os.path.dirname(__file__)

skater_file = os.path.join(dirname, '../data/skaters/21-22_skaters.csv')
skaters_df = pd.read_csv(skater_file, index_col='playerId', header=0)

# Find players that played on 5-on-5 basis
situation = skaters_df[skaters_df['situation'] == '5on5']
skaters5on5 = pd.DataFrame(situation)

skaters5on5.to_csv('../data/skaters/5on5.csv')

# # Extract players Ids in order to use them for similar name/lastname
# skaters_df = pd.concat([skaters5on5["name"], skaters5on5["playerId"]], axis=1)
# skatersdf_5on5 = skaters_df.drop_duplicates("playerId")


# for each node find all lines they played on
# Read all lines from Lines.csv files
line_file = os.path.join(dirname, '../data/lines/21-22_lines.csv')

lines_df = pd.read_csv(line_file, index_col=None, header=0)


# Seperate lineID each player so we can replace the lastname of players with their full name
N = 7


def split_string(x): return pd.Series(
    [str(x)[i:i+N] for i in range(0, len(str(x)), N)])


new_var = lines_df['lineId'].apply(split_string).fillna('')
new_var.columns = 'playerId' + (new_var.columns + 1).astype(str).str.zfill(1)
linedf = lines_df.join(new_var)
linesdf = lines_df.copy(deep=True)

print(linedf)
print(linesdf)

# Replace the lastname of players with their full name
linesdf.rename(columns={'playerId1': 'playerId'}, inplace=True)
linesdf['playerId'] = linesdf['playerId'].astype(int64)
merged_df = linesdf.merge(skatersdf_5on5, how='left', on='playerId')
merged_df = linesdf.merge(skatersdf_5on5, how='left', on='playerId')
linesdf.rename(columns={'playerId': 'playerId1'}, inplace=True)
linesdf.rename(columns={'playerId2': 'playerId'}, inplace=True)
merged_df['playername1'] = merged_df['name_y']
linesdf['playerId'] = linesdf['playerId'].astype(int64)
merged_df2 = linesdf.merge(skatersdf_5on5, how='left', on='playerId')

merged_df2['playername2'] = merged_df2['name_y']
merged_df2['playername1'] = merged_df['playername1']
linesdf.rename(columns={'playerId': 'playerId2'}, inplace=True)
linesdf.rename(columns={'playerId3': 'playerId'}, inplace=True)
linesdf[linesdf['playerId'] == ''] = '0'
linesdf['playerId'] = linesdf['playerId'].astype(int64)
merged_df3 = linesdf.merge(skatersdf_5on5, how='left', on='playerId')
merged_df3['playername3'] = merged_df3['name_y']
merged_df3['playername1'] = merged_df['playername1']
merged_df3['playername2'] = merged_df2['playername2']
final_Lines_df = merged_df3.copy()
final_Lines_df['player names'] = final_Lines_df.apply(
    lambda x: '%s-%s-%s' % (x['playername1'], x['playername2'], x['playername3']), axis=1)
# print(final_Lines_df)

# Save new data in a csv file
final_Lines_df.to_csv('../data/cleanedLines.csv')
