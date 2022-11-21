import pandas as pd
import glob
import os
import numpy as np
from numpy import int64

# Read all players from skaters.csv files
dirname = os.path.dirname(__file__)

skaters_dir = os.path.join(dirname, '../data/skaters/')
skaters_files = glob.glob(skaters_dir + '*.csv')


def format_skater_df(df):
    situation = df[df['situation'] == '5on5']
    df = pd.DataFrame(situation)
    position = df[df['position'] != 'D']
    df = pd.DataFrame(position)
    # drop position and team as they may change from season to season
    df = df.drop(
        columns=['season', 'team', 'position', 'situation'])
    df = df.rename(columns={'name': 'playerName'})
    return df


# aggregate skater data over our time period
skater_file = os.path.join(dirname, '../data/skaters/21-22_skaters.csv')
skaters_files.remove(skater_file)
skaters_df = pd.read_csv(skater_file, index_col='playerId', header=0)
skaters_df = format_skater_df(skaters_df)

print(skaters_files)


# combines current player row with dataframe
def add_player_data(player_row):
    id = player_row.name
    if player_row.name in skaters_df.index:
        updated_row = skaters_df.loc[id]
        total_icetime = updated_row.icetime + player_row.icetime
        updated_cfp = player_row.onIce_corsiPercentage * \
            (player_row.icetime / total_icetime) + \
            updated_row.onIce_corsiPercentage * \
            (updated_row.icetime / total_icetime)

        updated_row.games_played += player_row.games_played
        updated_row.icetime += player_row.icetime
        updated_row.onIce_corsiPercentage = updated_cfp
    else:
        updated_row = player_row
    return updated_row


for file in skaters_files:
    df = pd.read_csv(file, index_col='playerId', header=0)
    df = format_skater_df(df)
    updated_df = df.apply(add_player_data, axis=1)
    skaters_df = pd.concat([skaters_df, updated_df])
    skaters_df = skaters_df[~skaters_df.index.duplicated(keep='last')]

print(skaters_df)
skaters_df.to_csv('../data/aggregate_forwards.csv')