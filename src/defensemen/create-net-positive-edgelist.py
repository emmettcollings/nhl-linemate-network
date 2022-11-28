import pandas as pd
import glob
import os
import numpy as np
from numpy import int64

# calculate corsi influence for defensemen pairings
dirname = os.path.dirname(__file__)
defensemen_file = os.path.join(
    dirname, '../../data/defense/aggregate_defensemen.csv')
defensemen_df = pd.read_csv(defensemen_file, index_col='playerId', header=0)


def calculate_corsi_influence_pair(line_row):
    id1 = int(line_row.playerId1)
    id2 = int(line_row.playerId2)
    line_icetime = line_row.icetime
    line_cfp = line_row.corsiPercentage
    player_1_row = defensemen_df.loc[id1]
    player_2_row = defensemen_df.loc[id2]
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

    p2_inf_p1 = float(line_cfp - p2_cfp_without)
    p1_inf_p2 = float(line_cfp - p1_cfp_without)

    # if the influence is negligible we replace with 0 to avoid clutter
    if (abs(p2_inf_p1) < 1e-10):
        p2_inf_p1 = 0
    if (abs(p1_inf_p2) < 1e-10):
        p1_inf_p2 = 0
    return pd.Series([p1_inf_p2, p2_inf_p1])


# calculate influence players have on their partners
pairings_file = os.path.join(
    dirname, '../../data/defense/aggregate_pairings.csv')
pairings_df = pd.read_csv(pairings_file, index_col='lineId', header=0)

corsi_influence = pairings_df.apply(calculate_corsi_influence_pair, axis=1)
corsi_influence.columns = [
    'corsi_influence_on_player1', 'corsi_influence_on_player2']
corsi_pairings_df = pairings_df.join(corsi_influence)

# Full edgelist
# Do we adjust scale to mean 4 stdDev 1 here? Might remove negative edges entirely
# and process improvements/hindrances separately.
corsi_stdDev = defensemen_df['onIce_corsiPercentage'].std()
corsi_pairings_df['corsi_influence_on_player1_stdDevs'] = corsi_pairings_df.apply(
    lambda row: (row.corsi_influence_on_player1 / corsi_stdDev) + 4, axis=1)
corsi_pairings_df['corsi_influence_on_player2_stdDevs'] = corsi_pairings_df.apply(
    lambda row: (row.corsi_influence_on_player2 / corsi_stdDev) + 4, axis=1)

# Net positive
# This is to determine whether a combo is net positive or negative
net_positive_df = corsi_pairings_df
net_positive_df['combined_corsi_influence'] = net_positive_df.apply(
    lambda row: row.corsi_influence_on_player1 + row.corsi_influence_on_player2, axis=1)

# drop any edges that are net negative
net_positive_df = net_positive_df.drop(
    net_positive_df[net_positive_df.combined_corsi_influence < 0].index)

# save in new csv
output_file = os.path.join(
    dirname, '../../data/defense/defensemen_edgelist_corsi_net_positive.csv')
net_positive_df.to_csv(output_file)
