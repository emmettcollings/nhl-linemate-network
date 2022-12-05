import pandas as pd
import glob
import os
import numpy as np
from numpy import int64

# Read our data into dataframes
dirname = os.path.dirname(__file__)
forwards_file = os.path.join(
    dirname, '../../data/forwards/aggregate_forwards.csv')
forwards_df = pd.read_csv(forwards_file, index_col='playerId', header=0)
lines_file = os.path.join(dirname, '../../data/forwards/aggregate_lines.csv')
lines_df = pd.read_csv(lines_file, index_col='lineId', header=0)


id = 8481068
# Get list of lines current player has played on
df = lines_df[(lines_df['playerId1'] == id) | (
    lines_df['playerId2'] == id) | (lines_df['playerId3'] == id)]

print(df)
edgelist_df = pd.DataFrame(
    columns=[
        'pairId',
        'playerId1',
        'playerId2',
        'player1Name',
        'player2Name',
        'icetime',
        'cf_inf_on1',
        'cf_inf_on2'])


# Calculate corsi influence
def calculate_corsi_influence_pair(id1, id2, line_row):
    line_icetime = line_row.icetime
    line_cfp = line_row.corsiPercentage
    player_1_row = forwards_df.loc[id1]
    player_2_row = forwards_df.loc[id2]
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

    return pd.Series([p1_inf_p2, p2_inf_p1])


# Check if pair has an edge, then update list
def update_edge_list(pid1, pid2, line_row):
    global edgelist_df
    pairId1 = str(pid1) + str(pid2)
    pairId2 = str(pid2) + str(pid1)
    pairIds = []
    try:
        pairIds = edgelist_df['pairId'].to_numpy()
    except KeyError as ke:
        pass
    if pairId1 in pairIds or pairId2 in pairIds:
        # update existing edge for pair
        cfs = calculate_corsi_influence_pair(pid1, pid2, line_row)
        print(cfs)
    else:
        # Make new edge for pair
        cfs = calculate_corsi_influence_pair(pid1, pid2, line_row)
        new_row = {
            'pairId': pairId1,
            'playerId1': pid1,
            'playerId2': pid2,
            'player1Name': forwards_df.loc[pid1].playerName,
            'player2Name': forwards_df.loc[pid2].playerName,
            'icetime': line_row.icetime,
            'cf_inf_on1': cfs[0],
            'cf_inf_on2': cfs[1]}
        edgelist_df = edgelist_df.append(new_row, ignore_index=True)


# Check pairs of players on a line
def process_edges(line_row):
    # Check if edge exists between current player and p1
    if id != line_row.playerId1:
        update_edge_list(id, line_row.playerId1, line_row)
    if id != line_row.playerId2:
        update_edge_list(id, line_row.playerId2, line_row)
    if id != line_row.playerId3:
        update_edge_list(id, line_row.playerId3, line_row)


df.apply(process_edges, axis=1)
print(edgelist_df)

# def calculate_corsi_influence_pair(line_row):
#     id1 = int(line_row.playerId1)
#     id2 = int(line_row.playerId2)
#     line_icetime = line_row.icetime
#     line_cfp = line_row.corsiPercentage
#     player_1_row = forwards_df.loc[id1]
#     player_2_row = forwards_df.loc[id2]
#     p1_icetime = player_1_row.icetime
#     p2_icetime = player_2_row.icetime
#     p1_cfp = player_1_row.onIce_corsiPercentage
#     p2_cfp = player_2_row.onIce_corsiPercentage

#     p1_time_with_prop = line_icetime / p1_icetime
#     p2_time_with_prop = line_icetime / p2_icetime
#     p1_time_without_prop = 1 - p1_time_with_prop
#     p2_time_without_prop = 1 - p2_time_with_prop

#     p1_cfp_without = (p1_cfp - line_cfp * p1_time_with_prop) / \
#         p1_time_without_prop
#     p2_cfp_without = (p2_cfp - line_cfp * p2_time_with_prop) / \
#         p2_time_without_prop

#     p2_inf_p1 = float(line_cfp - p2_cfp_without)
#     p1_inf_p2 = float(line_cfp - p1_cfp_without)

#     # if the influence is negligible we replace with 0 to avoid clutter
#     if (abs(p2_inf_p1) < 1e-10):
#         p2_inf_p1 = 0
#     if (abs(p1_inf_p2) < 1e-10):
#         p1_inf_p2 = 0
#     return pd.Series([p1_inf_p2, p2_inf_p1])


# # calculate influence players have on their partners
# pairings_file = os.path.join(
#     dirname, '../../data/defense/aggregate_pairings.csv')
# pairings_df = pd.read_csv(pairings_file, index_col='lineId', header=0)

# corsi_influence = pairings_df.apply(calculate_corsi_influence_pair, axis=1)
# corsi_influence.columns = [
#     'corsi_influence_on_player1', 'corsi_influence_on_player2']
# corsi_pairings_df = pairings_df.join(corsi_influence)

# # Full edgelist
# corsi_stdDev = forwards_df['onIce_corsiPercentage'].std()
# corsi_pairings_df['corsi_influence_on_player1_stdDevs'] = corsi_pairings_df.apply(
#     lambda row: (row.corsi_influence_on_player1 / corsi_stdDev), axis=1)
# corsi_pairings_df['corsi_influence_on_player2_stdDevs'] = corsi_pairings_df.apply(
#     lambda row: (row.corsi_influence_on_player2 / corsi_stdDev), axis=1)

# # This is to determine whether a combo is net positive or negative
# net_positive_df = corsi_pairings_df
# net_positive_df['combined_corsi_influence'] = net_positive_df.apply(
# lambda row: row.corsi_influence_on_player1 +
# row.corsi_influence_on_player2, axis=1)

# # save in new csv
# output_file = os.path.join(
#     dirname, '../../data/defense/defensemen_edgelist_corsi.csv')
# corsi_pairings_df.to_csv(output_file)
