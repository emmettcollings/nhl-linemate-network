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

edgelist_df = pd.DataFrame(
    columns=[
        'pairId',
        'playerId1',
        'playerId2',
        'player1Name',
        'player2Name',
        'icetime',
        'corsiPercentage',
        'cf_inf_on1',
        'cf_inf_on2',
        'cf_inf_on1_std',
        'cf_inf_on2_std'])


for id in forwards_df.index:
    # Get list of lines current player has played on
    df = lines_df[(lines_df['playerId1'] == id) | (
        lines_df['playerId2'] == id) | (lines_df['playerId3'] == id)]

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

    def update_edge(edge, line_row):
        edge_pair_icetime = edge.icetime + line_row.icetime
        edge_pair_corsi = edge.corsiPercentage * \
            (edge.icetime / edge_pair_icetime) + line_row.corsiPercentage * (line_row.icetime / edge_pair_icetime)

        edge.icetime = edge_pair_icetime
        edge.corsiPercentage = edge_pair_corsi
        cfs = calculate_corsi_influence_pair(
            int(edge.playerId1), int(edge.playerId2), edge)
        edge.cf_inf_on1 = cfs[0]
        edge.cf_inf_on2 = cfs[1]
        return edge

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
            if pairId1 in pairIds:
                edge = edgelist_df.loc[edgelist_df["pairId"] == pairId1]
            else:
                edge = edgelist_df.loc[edgelist_df["pairId"] == pairId2]
            edge = update_edge(edge, line_row)
            edgelist_df.loc[edge.index] = edge
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
                'corsiPercentage': line_row.corsiPercentage,
                'cf_inf_on1': cfs[0],
                'cf_inf_on2': cfs[1],
                'cf_inf_on1_std': 5 + cfs[0] / np.std(forwards_df['onIce_corsiPercentage']),
                'cf_inf_on2_std': 5 + cfs[1] / np.std(forwards_df['onIce_corsiPercentage'])}
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


# edgelist_df['cf_inf_on1'] = edgelist_df.apply(lambda row: row.cf_inf_on1 * - 1, axis=1)
# edgelist_df['cf_inf_on2'] = edgelist_df.apply(lambda row: row.cf_inf_on2 * - 1, axis=1)

# save in new csv
output_file = os.path.join(
    dirname, '../../data/forwards/forwards_edgelist_corsi.csv')
edgelist_df.to_csv(output_file)
