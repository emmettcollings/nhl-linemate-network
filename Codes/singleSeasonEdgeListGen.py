import pandas as pd
import glob
import os
import numpy as np
from numpy import int64

# Read all skater players from skaters.csv files
dirname = os.path.dirname(__file__)

skater_file = os.path.join(dirname, '../data/skaters/21-22_skaters.csv')
skaters_df = pd.read_csv(skater_file, index_col=None, header=0)

# Find players that played on 5-on-5 basis
situation = skaters_df[skaters_df['situation'] == '5on5']
skaters5on5 = pd.DataFrame(situation)

skaters5on5.to_csv('../data/2021_5on5.csv')

# for each node find all lines they played on
# Read all lines from Lines.csv files
line_file = os.path.join(dirname, '../data/lines/21-22_lines.csv')

raw_lines_df = pd.read_csv(line_file, index_col=None, header=0)
raw_lines_df = raw_lines_df.drop(columns=['season'])

# Separate lineID each player so we can replace the lastname of players with their full name


def split_string(x): return pd.Series(
    [x[i:i+7] for i in range(0, len(x), 7)])


new_var = raw_lines_df['lineId'].apply(split_string).fillna('')
new_var.columns = 'playerId' + (new_var.columns + 1).astype(str).str.zfill(1)
line_df = raw_lines_df.join(new_var)
line_df.to_csv('../data/2021_linesIds.csv')

# extract pairings only
pairings = line_df[line_df['position'] == 'pairing']
pairings_df = pd.DataFrame(pairings)
pairings_df.to_csv('../data/2021_pairings.csv')


# calculate corsi influence for pairings
def calculate_corsi_influence(line_row):
    line_icetime = line_row['icetime']
    line_cfp = line_row['corsiPercentage']
    player_1_row = skaters5on5[skaters5on5['playerId']
                               == int(line_row['playerId1'])]
    player_2_row = skaters5on5[skaters5on5['playerId']
                               == int(line_row['playerId2'])]
    p1_icetime = player_1_row['icetime']
    p2_icetime = player_2_row['icetime']
    p1_cfp = player_1_row['onIce_corsiPercentage']
    p2_cfp = player_2_row['onIce_corsiPercentage']

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
corsi_influence = pairings_df.apply(calculate_corsi_influence, axis=1)
corsi_influence.columns = [
    'corsi_influence_on_player2', 'corsi_influence_on_player_1']
corsi_pairings_df = pairings_df.join(corsi_influence)

# save in new csv
corsi_pairings_df.to_csv('../data/2021_pairings_corsi.csv')
