import glob
import os

import pandas as pd

dirname = os.path.dirname(__file__)

# aggregate lines data
lines_dir = os.path.join(dirname, '../../../data/raw/lines/')
lines_files = glob.glob(lines_dir + '*.csv')


# format lines dataframes
def format_lines_df(df):
    situation = df[df['situation'] == '5on5']
    df = pd.DataFrame(situation)
    pairings = df[df['position'] != 'pairing']
    df = pd.DataFrame(pairings)
    df = df.drop(
        columns=['season', 'iceTimeRank', 'team', 'situation'])

    df = df.rename(columns={'name': 'playerNames'})
    return df


lines_file = os.path.join(dirname, '../../../data/raw/lines/21-22_lines.csv')
lines_files.remove(lines_file)
lines_df = pd.read_csv(lines_file, index_col='lineId', header=0)
lines_df = format_lines_df(lines_df)

print(lines_files)


# combines current line row with dataframe
def add_line_data(line_row):
    id = line_row.name
    if line_row.name in lines_df.index:
        updated_row = lines_df.loc[id]
        total_icetime = updated_row.icetime + line_row.icetime
        updated_cfp = line_row.corsiPercentage * \
            (line_row.icetime / total_icetime) + \
            updated_row.corsiPercentage * \
            (updated_row.icetime / total_icetime)

        updated_row.games_played += line_row.games_played
        updated_row.icetime += line_row.icetime
        # corsi
        updated_row.corsiPercentage = updated_cfp
    else:
        updated_row = line_row
    return updated_row


for file in lines_files:
    df = pd.read_csv(file, index_col='lineId', header=0)
    df = format_lines_df(df)
    updated_df = df.apply(add_line_data, axis=1)
    lines_df = pd.concat([lines_df, updated_df])
    lines_df = lines_df[~lines_df.index.duplicated(keep='last')]

# drop any lines that have less than 100 minutes (6000s) of icetime
lines_df = lines_df.drop(lines_df[lines_df.icetime < 6000].index)


# Separate lineId into playerIds
def split_string(x):
    return pd.Series([x[i:i + 7] for i in range(0, len(x), 7)])


split_ids = lines_df.index.to_series().apply(
    split_string).fillna('')  # Returns pd.Series
split_ids.columns = 'playerId' + \
    (split_ids.columns + 1).astype(str).str.zfill(1)
lines_df = lines_df.join(split_ids)

# add full player names
forwards_file = os.path.join(
    dirname, '../../../data/interim/aggregated_forwards.csv')
forwards_df = pd.read_csv(forwards_file, index_col='playerId', header=0)
lines_df['player1Name'] = lines_df.apply(
    lambda x: forwards_df.loc[int(x.playerId1)].playerName, axis=1)
lines_df['player2Name'] = lines_df.apply(
    lambda x: forwards_df.loc[int(x.playerId2)].playerName, axis=1)
lines_df['player3Name'] = lines_df.apply(
    lambda x: forwards_df.loc[int(x.playerId3)].playerName, axis=1)

# Write to file
output_file = os.path.join(
    dirname, '../../../data/interim/aggregated_lines.csv')
lines_df.to_csv(output_file)
output_file = os.path.join(
    dirname, '../../../data/final/aggregated_lines.csv')
lines_df.to_csv(output_file)