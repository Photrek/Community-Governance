"""Module for extracting JSON data from a Swae data export."""

import glob
import json
import os
import shutil
import tempfile
from typing import Any, Dict, List


def extract_swae_data(zip_filepath: str) -> Dict[str, Any]:
    """Extract JSON data from a ZIP file that comes from a Swae data export.

    Parameters
    ----------
    zip_filepath : str
        The path of the ZIP file, which contains a data export of Swae
        in form of multiple JSON files.

    Returns
    -------
    swae_data : Dict[str, Any]
        A dictionary containing the extracted JSON data.

    Raises
    ------
    FileNotFoundError
        If the ZIP file does not exist.
        If an expected JSON file is not contained in it.
    ValueError
        If there are errors in loading or processing the JSON files.

    """
    # Create a temporary directory that is deleted after the block
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract the ZIP file into the temporary directory
        _unzip_file(zip_filepath, temp_dir)

        # Detect the filepath for each filename
        filenames = [
            "missions.json",
            "proposals.json",
            "users.json",
            "votesByProposalId.json",
            "commentsByProposalId.json",
            "reactionsByCommentIdByType.json",
            "upvotesByCommentId.json",
            "downvotesByCommentId.json",
            "viewsByProposalId.json",
        ]
        filepaths = _find_filepaths(temp_dir, filenames)

        # Load data from each file
        raw_data = {fn: _load_json_file(fp) for fn, fp in zip(filenames, filepaths)}

    # Associate data with simpler names
    data = {
        "missions": raw_data["missions.json"],
        "proposals": raw_data["proposals.json"],
        "users": raw_data["users.json"],
        "ratings_by_proposal": raw_data["votesByProposalId.json"],
        "comments_by_proposal": raw_data["commentsByProposalId.json"],
        "reactions_by_comment_by_type": raw_data["reactionsByCommentIdByType.json"],
        "upvotes_by_comment": raw_data["upvotesByCommentId.json"],
        "downvotes_by_comment": raw_data["downvotesByCommentId.json"],
        "views_by_proposal": raw_data["viewsByProposalId.json"],
    }

    # Flatten nested data
    data["ratings"] = _flatten_list(data["ratings_by_proposal"].values())
    data["comments"] = _flatten_list(data["comments_by_proposal"].values())
    data["upvotes"] = _flatten_list(data["upvotes_by_comment"].values())
    data["downvotes"] = _flatten_list(data["downvotes_by_comment"].values())
    data["views"] = _flatten_list(data["views_by_proposal"].values())

    # Flatten doubly nested data
    reactions = []
    for some_reactions_by_comment in data["reactions_by_comment_by_type"].values():
        for some_reactions in some_reactions_by_comment.values():
            if len(some_reactions) > 0:
                reactions.extend(some_reactions)
    data["reactions"] = reactions
    return data


def _unzip_file(source_filepath: str, target_dirpath: str) -> None:
    """Unpack the contents of a ZIP file into a given target directory.

    Parameters
    ----------
    source_filepath : str
        The path of the ZIP file.
    target_dirpath : str
        The path of the target directory.

    Raises
    ------
    FileNotFoundError
        If the source file does not exist.
        If the target directory does not exist after the extraction process.
    ValueError
        If there are errors during the extraction process.

    """
    # Precondition: ZIP file exists
    if not os.path.isfile(source_filepath):
        message = f"Source file could not be found.\nGiven path: {source_filepath}"
        raise FileNotFoundError(message)

    # Unpack the ZIP file into the target directory
    try:
        shutil.unpack_archive(source_filepath, target_dirpath)
    except Exception as e:
        raise ValueError(f"Error during unpacking the ZIP file: {e}")

    # Postcondition: Target directory exists
    if not os.path.isdir(target_dirpath):
        message = f"Target directory was not generated.\nGiven path: {target_dirpath}"
        raise FileNotFoundError(message)


def _find_filepaths(dirpath: str, filenames: List[str]) -> List[str]:
    """Find the filepaths of given filenames within a directory and its subdirectories.

    Parameters
    ----------
    dirpath : str
        The path of the directory in which the search for filenames takes place.
    filenames : List[str]
        A list of filenames to search for.

    Returns
    -------
    filepaths : List[str]
        A list of filepaths.

    Raises
    ------
    FileNotFoundError
        If the specified directory does not exist.
        If a given filename cannot be found within the directory and its subdirectories.

    """
    # Precondition: Directory exists
    if not os.path.isdir(dirpath):
        message = f"Directory could not be found.\nGiven path: {dirpath}"
        raise FileNotFoundError(message)

    # Find filepaths
    filepaths = []
    for fn in filenames:
        pattern = os.path.join(dirpath, "**", str(fn))
        found_filepaths = glob.glob(pattern, recursive=True)
        if len(found_filepaths) == 0:
            message = (
                "Filename could not be found in the given directory and its subdirectories."
                f"\nGiven directory: {dirpath}\nGiven filename: {fn}."
            )
            raise FileNotFoundError(message)
        chosen_filepath = found_filepaths[0]
        filepaths.append(chosen_filepath)
    return filepaths


def _load_json_file(filepath: str) -> Any:
    """Load the content of a JSON file and return that data.

    Parameters
    ----------
    filepath : str
        The path of the JSON file.

    Returns
    -------
    data : Any
        The content of the JSON file, deserialized as Python objects.

    Raises
    ------
    FileNotFoundError
        If the JSON file does not exist.
    ValueError
        If the JSON file can not be loaded, e.g. due to content in an invalid format.

    """
    # Precondition: JSON file exists
    if not os.path.isfile(filepath):
        message = f"JSON file could not be found.\nGiven path: {filepath}"
        raise FileNotFoundError(message)

    # Load data
    try:
        with open(filepath) as f:
            return json.load(f)
    except Exception:
        message = (
            "JSON file could not be loaded. "
            f"The content might not to be in JSON format.\nGiven path: {filepath}"
        )
        raise ValueError(message)


def _flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """Flatten a nested list.

    Parameters
    ----------
    nested_list : List[List[Any]]
        The nested list to be flattened.

    Returns
    -------
    flat_list : List[Any]
        The flattened list.

    """
    return [item for sub_list in nested_list for item in sub_list]
