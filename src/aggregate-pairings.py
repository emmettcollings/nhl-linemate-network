import pandas as pd
import glob
import os
import numpy as np
from numpy import int64

# Read all skater players from skaters.csv files
dirname = os.path.dirname(__file__)

skaters_dir = os.path.join(dirname, '../data/skaters/')
skaters_files = glob.glob(skaters_dir + '*.csv')


def format_skater_df(df):
    situation = df[df['situation'] == '5on5']
    df = pd.DataFrame(situation)
    df = df.drop(
        columns=['season', 'team', 'position', 'situation'])
    df = df.rename(columns={'name': 'playerName'})
    return df


# aggregate skater data so we can make nodes
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
skaters_df.to_csv('../data/aggregate_skaters.csv')

# aggregate lines data
lines_dir = os.path.join(dirname, '../data/lines/')
lines_files = glob.glob(lines_dir + '*.csv')


# format lines dataframes
def format_lines_df(df):
    situation = df[df['situation'] == '5on5']
    df = pd.DataFrame(situation)
    df = df.drop(
        columns=['season', 'team', 'situation'])
    df = df.rename(columns={'name': 'playerNames'})
    return df


lines_file = os.path.join(dirname, '../data/lines/21-22_lines.csv')
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


# Separate lineId into playerIds
def split_string(x): return pd.Series(
    [x[i:i+7] for i in range(0, len(x), 7)])


split_ids = lines_df.index.to_series().apply(
    split_string).fillna('')  # Returns pd.Series
split_ids.columns = 'playerId' + \
    (split_ids.columns + 1).astype(str).str.zfill(1)
lines_df = lines_df.join(split_ids)

# add full player names
lines_df['player1Name'] = lines_df.apply(
    lambda x: skaters_df.loc[int(x.playerId1)].playerName, axis=1)
lines_df['player2Name'] = lines_df.apply(
    lambda x: skaters_df.loc[int(x.playerId2)].playerName, axis=1)
print(lines_df)
lines_df.to_csv('../data/aggregate_lines.csv')

# extract pairings only
pairings = lines_df[lines_df['position'] == 'pairing']
pairings_df = pd.DataFrame(pairings)
pairings_df = pairings_df.drop(columns=['playerId3'])
pairings_df.to_csv('../data/aggregate_pairings.csv')


# calculate corsi influence for pairings
def calculate_corsi_influence_pair(line_row):
    id1 = int(line_row.playerId1)
    id2 = int(line_row.playerId2)
    line_icetime = line_row.icetime
    line_cfp = line_row.corsiPercentage
    player_1_row = skaters_df.loc[id1]
    player_2_row = skaters_df.loc[id2]
    p1_icetime = player_1_row.icetime
    p2_icetime = player_2_row.icetime
    p1_cfp = player_1_row.onIce_corsiPercentage
    p2_cfp = player_2_row.onIce_corsiPercentage

    p1_time_with_prop = line_icetime / p1_icetime
    p2_time_with_prop = line_icetime / p2_icetime
    p1_time_without_prop = 1 - p1_time_with_prop
    p2_time_without_prop = 1 - p2_time_with_prop

    p1_cfp_without = (p1_cfp - line_cfp * p1_time_with_prop) / \
        p1_time_without_prop
    p2_cfp_without = (p2_cfp - line_cfp * p2_time_with_prop) / \
        p2_time_without_prop

    p1_inf_p2 = float(line_cfp - p2_cfp_without)
    p2_inf_p1 = float(line_cfp - p1_cfp_without)

    # if the influence is negligible we replace with 0 to avoid clutter
    if (abs(p1_inf_p2) < 1e-10):
        p1_inf_p2 = 0
    if (abs(p2_inf_p1) < 1e-10):
        p2_inf_p1 = 0
    return pd.Series([p1_inf_p2, p2_inf_p1])


# calculate influence players have on their partners
corsi_influence = pairings_df.apply(calculate_corsi_influence_pair, axis=1)
corsi_influence.columns = [
    'corsi_influence_on_player1', 'corsi_influence_on_player2']
corsi_pairings_df = pairings_df.join(corsi_influence)


# save in new csv
corsi_pairings_df.to_csv('../data/aggregate_pairings_corsi.csv')
