import os
import random
import shutil
import string

import pytest


JSON_FILEPATH = os.path.join("input", "test.json")
ZIP_FILEPATH = os.path.join("input", "raw.zip")


def test_unzip_file():
    from ces.swae_analysis.extract import _unzip_file

    random_dirpath = "".join(random.choice(string.ascii_letters) for _ in range(30))

    # desired functionality
    _unzip_file(ZIP_FILEPATH, random_dirpath)
    assert os.listdir(random_dirpath)
    shutil.rmtree(random_dirpath, ignore_errors=True)

    # desired exceptions
    with pytest.raises(FileNotFoundError):
        _unzip_file("nonexistent_zip_file", random_dirpath)
    with pytest.raises(ValueError):
        _unzip_file(ZIP_FILEPATH, "/target_directory_without_write_permission")


def test_find_filepaths():
    from ces.swae_analysis.extract import _find_filepaths

    # desired functionality
    filepaths = _find_filepaths(".", ["test_units.py"])
    assert isinstance(filepaths, list)
    assert isinstance(filepaths[0], str)
    assert len(filepaths) == 1

    # desired exceptions
    with pytest.raises(FileNotFoundError):
        _find_filepaths(".", ["nonexistent_file"])
    with pytest.raises(FileNotFoundError):
        _find_filepaths("nonexistent_source", ["file1", "file2"])


def test_load_json_file():
    from ces.swae_analysis.extract import _load_json_file

    # desired functionality
    data = _load_json_file(JSON_FILEPATH)
    assert data == [1, 2, "a", "b"]

    # desired exceptions
    with pytest.raises(FileNotFoundError):
        _load_json_file("nonexistent_source")
    with pytest.raises(ValueError):
        _load_json_file(ZIP_FILEPATH)


def test_flatten_list():
    from ces.swae_analysis.extract import _flatten_list

    nested = [[1, 2], [3], [4, 5, 6]]
    flat = [1, 2, 3, 4, 5, 6]
    assert _flatten_list(nested) == flat

    nested = [["ab"], ["c"], ["d", "e"], ["f", "g"], ["hi", "j"]]
    flat = ["ab", "c", "d", "e", "f", "g", "hi", "j"]
    assert _flatten_list(nested) == flat


def test_etl(tmpdir):
    from ces.swae_analysis.extract import extract_swae_data
    from ces.swae_analysis.load import load_sqlite
    from ces.swae_analysis.transform import transform_swae_data

    json_data = extract_swae_data(ZIP_FILEPATH)
    tabular_data = transform_swae_data(json_data)
    con = load_sqlite(tabular_data)
    con.close()

    for _ in range(2):
        dirpath = os.path.join(tmpdir, "somesubdir")
        filepath = os.path.join(dirpath, "test.sqlite")
        con = load_sqlite(tabular_data, filepath)
        assert os.path.isfile(filepath)
        con.close()
