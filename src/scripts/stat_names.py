"""_summary_
Reads
"""

import csv
import os


def to_snake_case(string: str):
    """_summary_

    Args:
        string (str): _description_

    Returns:
        _type_: _description_
    """
    print("Converting to snake case" + string)
    snaked = string
    return snaked


dirname = os.path.dirname(__file__)
skaters_file = os.path.join(dirname, "../../data/raw/skaters/21-22_skaters.csv")

# Open the CSV file and read the contents
with open(skaters_file, "r", encoding="utf-8") as f:
    reader = csv.reader(f)

    # Get the column labels from the first row
    headers = next(reader)

    # Create an empty dictionary
    data = {}

    # Iterate through the headers and translate to snake case
    for stat in headers:
        data[stat] = to_snake_case(stat)

# The dictionary is now populated with the data from the CSV file
print(data)
