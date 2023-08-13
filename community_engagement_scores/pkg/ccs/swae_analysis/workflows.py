import tempfile

from .extract import extract_swae_data
from .load import load_dataframes, load_sqlite
from .transform import transform_swae_data


def zip_to_sqlite(source_filepath, target_filepath):
    # TODO: docstring
    with tempfile.TemporaryDirectory() as temp_dir:
        json_data = extract_swae_data(source_filepath, temp_dir)

    tabular_data = transform_swae_data(json_data)
    conn = load_sqlite(tabular_data, target_filepath)
    return conn


def zip_to_dataframes(source_filepath):
    # TODO: docstring
    with tempfile.TemporaryDirectory() as temp_dir:
        json_data = extract_swae_data(source_filepath, temp_dir)

    tabular_data = transform_swae_data(json_data)
    dfs = load_dataframes(tabular_data)
    return dfs
