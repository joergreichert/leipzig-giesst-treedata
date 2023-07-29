import datetime

from treedata.radolan.update_tree_radolan_days import get_sorted_cleaned_grid
import os
import pandas as pd

ROOT_DIR = os.path.abspath(os.curdir)


def test_get_sorted_cleaned_grid():
    path = f'{ROOT_DIR}/resources_test/radolan/weather_data_grid_cells.csv'
    columns = ["id", "st_asgeojson", "measured_at", "value"]
    df = pd.read_csv(path, sep=";", names=columns)
    grid = []
    for _, row in df.iterrows():
        grid.append([row[0], row[1],
                     [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in row[2].split(",")],
                     [int(x) for x in row[3].split(",")]])
    now = datetime.datetime(2023, 7, 28, 15, 47, 30)
    timelimit_days = 30
    cleaned = get_sorted_cleaned_grid(grid, timelimit_days, now)
    assert len(cleaned) > 0
    # values of row 8 in csv
    assert cleaned[7][27] == 3
    assert cleaned[7][28] == 6
