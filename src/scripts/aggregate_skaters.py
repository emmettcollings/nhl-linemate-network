"""_summary_
Aggregates the statistics of all players over all seasons, combining into one
master file. Only 5v5 statistics are considered, and teams and positions are
dropped as they are subject to change between seasons.

Inputs:
    data/raw/skaters/: Iterates over all csvs in this data folder.
Outputs:
    aggregated_skaters.csv: All skaters' data over our time period.
"""

import glob
import os

import pandas as pd

# Read all players from skaters.csv files
dirname = os.path.dirname(__file__)

skaters_dir = os.path.join(dirname, "../../data/raw/skaters/")
skaters_files = glob.glob(skaters_dir + "*.csv")
print(skaters_files)


def format_skater_df(season_skaters_df):
    """_summary_

    Args:
        season_skaters_df (_type_): _description_

    Returns:
        _type_: _description_
    """
    situation = season_skaters_df[season_skaters_df["situation"] == "5on5"]
    season_skaters_df = pd.DataFrame(situation)
    # drop position and team as they may change from season to season
    season_skaters_df = season_skaters_df.drop(
        columns=["season", "team", "position", "situation"]
    )
    season_skaters_df = season_skaters_df.rename(columns={"name": "playerName"})
    return season_skaters_df


# aggregate skater data over our time period
skater_file = os.path.join(dirname, "../../data/raw/skaters/21-22_skaters.csv")
skaters_files.remove(skater_file)
skaters_df = pd.read_csv(skater_file, index_col="playerId", header=0)
skaters_df = format_skater_df(skaters_df)


# combines current player row with data frame
def add_player_data(player_row):
    """_summary_

    Args:
        player_row (_type_): _description_

    Returns:
        _type_: _description_
    """
    player_id = player_row.name
    if player_row.name in skaters_df.index:
        updated_row = skaters_df.loc[player_id]

        # use for updating stats expressed as percentages
        total_icetime = updated_row.icetime + player_row.icetime
        total_timeOnBench = updated_row.timeOnBench + player_row.timeOnBench

        # on ice corsi percentage
        updated_on_ice_corsi = player_row.onIce_corsiPercentage * (
            player_row.icetime / total_icetime
        ) + updated_row.onIce_corsiPercentage * (updated_row.icetime / total_icetime)

        # off ice corsi percentage
        updated_off_ice_corsi = player_row.offIce_corsiPercentage * (
            player_row.timeOnBench / total_timeOnBench
        ) + updated_row.offIce_corsiPercentage * (
            updated_row.timeOnBench / total_timeOnBench
        )

        updated_row.games_played += player_row.games_played
        updated_row.icetime += player_row.icetime
        updated_row.timeOnBench += player_row.timeOnBench
        # corsi on and off ice
        updated_row.onIce_corsiPercentage = updated_on_ice_corsi
        updated_row.offIce_corsiPercentage = updated_off_ice_corsi
        # on ice goals for
        updated_row.OnIce_F_goals += player_row.OnIce_F_goals
        # on ice goals agains
        updated_row.OnIce_A_goals += player_row.OnIce_A_goals
        # individual d zone giveaways
        updated_row.I_F_dZoneGiveaways += player_row.I_F_dZoneGiveaways
        # individual giveaways
        updated_row.I_F_giveaways += player_row.I_F_giveaways
        # individual hits
        updated_row.I_F_hits += player_row.I_F_hits
        # individual takeaways
        updated_row.I_F_takeaways += player_row.I_F_takeaways
        # points
        updated_row.I_F_points += player_row.I_F_points
        # shots blocked
        updated_row.shotsBlockedByPlayer += player_row.shotsBlockedByPlayer
        # o zone shift starts
        updated_row.I_F_oZoneShiftStarts += player_row.I_F_oZoneShiftStarts
        # d zone shift starts
        updated_row.I_F_dZoneShiftStarts += player_row.I_F_dZoneShiftStarts
        # neutral zone shift starts
        updated_row.I_F_neutralZoneShiftStarts += player_row.I_F_neutralZoneShiftStarts
        # fly shift starts
        updated_row.I_F_flyShiftStarts += player_row.I_F_flyShiftStarts
        # primary assists
        updated_row.I_F_primaryAssists += player_row.I_F_primaryAssists
        # secondary assists
        updated_row.I_F_secondaryAssists += player_row.I_F_secondaryAssists
        # individual goals
        updated_row.I_F_goals += player_row.I_F_goals
    else:
        updated_row = player_row
    return updated_row


for file in skaters_files:
    df = pd.read_csv(file, index_col="playerId", header=0)
    df = format_skater_df(df)
    updated_df = df.apply(add_player_data, axis=1)
    skaters_df = pd.concat([skaters_df, updated_df])
    skaters_df = skaters_df[~skaters_df.index.duplicated(keep="last")]


# compute some new stats that may be of use to us
# Difference in team corsi when player is on. Conceptually seems indicative of
# a player being much better than their teammates or otherwise important to the
# team's success
skaters_df["on_off_corsi_diff"] = skaters_df.apply(
    lambda row: row.onIce_corsiPercentage - row.offIce_corsiPercentage, axis=1
)

# Team goals for per 60
skaters_df["OnIce_F_goals_per60"] = skaters_df.apply(
    lambda row: (row.OnIce_F_goals / row.icetime) * 60 * 60, axis=1
)

# Opponent goals for per 60
skaters_df["OnIce_A_goals_per60"] = skaters_df.apply(
    lambda row: (row.OnIce_A_goals / row.icetime) * 60 * 60, axis=1
)

# D zone giveaways per 60
skaters_df["I_F_dZoneGiveaways_per60"] = skaters_df.apply(
    lambda row: (row.I_F_dZoneGiveaways / row.icetime) * 60 * 60, axis=1
)

# Giveaways per 60
skaters_df["I_F_giveaways_per60"] = skaters_df.apply(
    lambda row: (row.I_F_giveaways / row.icetime) * 60 * 60, axis=1
)

# Average TOI
skaters_df["average_TOI"] = skaters_df.apply(
    lambda row: row.icetime / row.games_played, axis=1
)

# Hits per 60
skaters_df["I_F_hits_per60"] = skaters_df.apply(
    lambda row: (row.I_F_hits / row.icetime) * 60 * 60, axis=1
)

# Takeaways per 60
skaters_df["I_F_takeaways_per60"] = skaters_df.apply(
    lambda row: (row.I_F_takeaways / row.icetime) * 60 * 60, axis=1
)

# Points per 60
skaters_df["I_F_points_per60"] = skaters_df.apply(
    lambda row: (row.I_F_points / row.icetime) * 60 * 60, axis=1
)

# Shots blocked per 60
skaters_df["shotsBlockedByPlayer_per60"] = skaters_df.apply(
    lambda row: (row.shotsBlockedByPlayer / row.icetime) * 60 * 60, axis=1
)

# O zone starts per 60
skaters_df["I_F_oZoneShiftStarts_per60"] = skaters_df.apply(
    lambda row: row.I_F_oZoneShiftStarts / row.icetime * 60 * 60, axis=1
)

# D zone starts per 60
skaters_df["I_F_dZoneShiftStarts_per60"] = skaters_df.apply(
    lambda row: row.I_F_dZoneShiftStarts / row.icetime * 60 * 60, axis=1
)

# Neutral zone starts per 60
skaters_df["I_F_neutralZoneShiftStarts_per60"] = skaters_df.apply(
    lambda row: row.I_F_neutralZoneShiftStarts / row.icetime * 60 * 60, axis=1
)

# Fly shift starts per 60
skaters_df["I_F_flyShiftStarts_per60"] = skaters_df.apply(
    lambda row: row.I_F_flyShiftStarts / row.icetime * 60 * 60, axis=1
)

# primary assists
skaters_df["I_F_primaryAssists_per60"] = skaters_df.apply(
    lambda row: row.I_F_primaryAssists / row.icetime * 60 * 60, axis=1
)

# secondary assists
skaters_df["I_F_secondaryAssists_per60"] = skaters_df.apply(
    lambda row: row.I_F_secondaryAssists / row.icetime * 60 * 60, axis=1
)

# individual assists
skaters_df["I_F_goals_per60"] = skaters_df.apply(
    lambda row: row.I_F_goals / row.icetime * 60 * 60, axis=1
)


interesting_stats = [
    "playerName",
    "games_played",
    "icetime",
    "timeOnBench",
    "onIce_corsiPercentage",
    "offIce_corsiPercentage",
    "on_off_corsi_diff",
    "OnIce_F_goals_per60",
    "OnIce_A_goals_per60",
    "I_F_dZoneGiveaways_per60",
    "I_F_giveaways_per60",
    "average_TOI",
    "I_F_hits_per60",
    "I_F_takeaways_per60",
    "I_F_points_per60",
    "shotsBlockedByPlayer_per60",
    "I_F_oZoneShiftStarts_per60",
    "I_F_dZoneShiftStarts_per60",
    "I_F_neutralZoneShiftStarts_per60",
    "I_F_flyShiftStarts_per60",
    "I_F_primaryAssists_per60",
    "I_F_secondaryAssists_per60",
    "I_F_goals_per60",
]

# Drop stats we don't aggregate
skaters_df = skaters_df[skaters_df.columns.intersection(interesting_stats)]

# Write to file
output_file = os.path.join(dirname, "../../data/interim/aggregated_skaters.csv")
skaters_df.to_csv(output_file)
output_file = os.path.join(dirname, "../../data/final/aggregated_skaters.csv")
skaters_df.to_csv(output_file)
