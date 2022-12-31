"""Makes stats more pythonic.

Reads stat names from a skater csv, then outputs a dictionary with the corresponding snake cased
stats.
"""

import csv
import os
import re
import json


def get_dirs():
    """Returns file names of stat json dump and skaters file

    Returns:
        2 strings: stat_file, skaters_file
    """

    dirname = os.path.dirname(__file__)
    stat_file = os.path.join(dirname, "../../data/stats_list.json")
    skaters_file = os.path.join(dirname, "../../data/raw/skaters/21-22_skaters.csv")
    return stat_file, skaters_file


def to_snake_case(string: str):
    """Makes a string snake_cased

    Args:
        string (str): string to be converted to snake case

    Returns:
        str: snake cased string
    """

    print("Converting '" + string + "' to snake case.")
    string = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", string).lower()


def get_stat_dict():
    """Returns list of stats and their snake cased forms

    Returns:
        dict: All the stats and snake case forms
    """

    stat_file, _ = get_dirs()
    print(stat_file)

    with open(stat_file, "r", encoding="utf-8") as ofile:
        stat_list = json.load(ofile)
    return stat_list


def write_stat_list():
    """Read stat names from skater csv, write dict with snake case to json file

    Outputs:
        .json: json dump of dict
    """

    stat_file, skaters_file = get_dirs()
    # Open the CSV file and read the contents
    with open(skaters_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)

        # Get the column labels from the first row
        headers = next(reader)

        # Create an empty dictionary
        stat_dict = {}

        # Iterate through the headers and translate to snake case
        for stat in headers:
            stat_dict[stat] = to_snake_case(stat)

        # Output dict as json in data folder
        with open(stat_file, "w", encoding="utf-8") as outfile:
            json.dump(stat_dict, outfile)

    return stat_dict


def write_stat_categories():
    """Writes stat categories for easier aggregation later"""
    print("Writing stat categories.")


# The dictionary is now populated with the data from the CSV file
data = write_stat_list()
print(data)
