import glob
import json
import os
import shutil
from typing import Any, Dict, List


def extract_swae_data(source_filepath: str, target_dirpath: str) -> Dict[str, Any]:
    """Extract raw JSON data from a Swae export, which comes in the form of a zip file.

    Parameters
    ----------
    source_filepath : str
        The path to the zip file to be extracted.

    target_dirpath : str
        The path to the target directory where the zip file will be extracted.

    Returns
    -------
    swae_data : Dict[str, Any]
        A dictionary containing the extracted JSON data from Swae.

    Raises
    ------
    FileNotFoundError
        If the zip file does not exist, an expected JSON file is not contained in it,
        or the target directory is not generated.
    ValueError
        If there are errors in loading or processing the JSON files.

    """
    # Extract the archive into a directory
    unzip_file(source_filepath, target_dirpath)

    # Detect filepath for each filename
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
    filepaths = find_filepaths(target_dirpath, filenames)

    # Load data from each file
    raw_data = {fn: load_json_file(fp) for fn, fp in zip(filenames, filepaths)}

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

    # Flatten grouped data
    data["ratings"] = flatten_list(data["ratings_by_proposal"].values())
    data["comments"] = flatten_list(data["comments_by_proposal"].values())
    data["upvotes"] = flatten_list(data["upvotes_by_comment"].values())
    data["downvotes"] = flatten_list(data["downvotes_by_comment"].values())
    data["views"] = flatten_list(data["views_by_proposal"].values())
    reactions = []
    for comment_id, reaction_list in data["reactions_by_comment_by_type"].items():
        for key, val in reaction_list.items():
            if len(val) > 0:
                reactions.extend(val)
    data["reactions"] = reactions
    return data


def flatten_list(nested_list: List[List]) -> List:
    """Flatten a nested list.

    Parameters
    ----------
    nested_list : List[List]
        The nested list to be flattened.

    Returns
    -------
    flat_list : List
        The flattened list.

    """
    return [item for sub_list in nested_list for item in sub_list]


def unzip_file(source_filepath: str, target_dirpath: str) -> None:
    """Unzip a file into a target directory.

    Parameters
    ----------
    source_filepath : str
        The path to the zip file to be unpacked.

    target_dirpath : str
        The path to the target directory where the contents of the zip file will be extracted.

    Raises
    ------
    FileNotFoundError
        If the source file does not exist or the target directory is not generated.

    """
    # Precondition: Zip file exists
    if not os.path.isfile(source_filepath):
        message = "Source file could not be found.\nGiven path: {}".format(
            source_filepath
        )
        raise FileNotFoundError(message)

    # Unpack the zip file into the target directory
    shutil.unpack_archive(source_filepath, target_dirpath)

    # Postcondition: Target directory exists
    if not os.path.isdir(target_dirpath):
        message = "Target directory was not generated.\nGiven path: {}".format(
            target_dirpath
        )
        raise FileNotFoundError(message)


def find_filepaths(dirpath: str, filenames: List[str]) -> List[str]:
    """Find the filepaths of given filenames within a directory and its subdirectories.

    Parameters
    ----------
    dirpath : str
        The path to the directory where the filenames will be searched.

    filenames : List[str]
        A list of filenames to search for within the directory and its subdirectories.

    Returns
    -------
    filepaths : List[str]
        A list of filepaths corresponding to the found filenames.

    Raises
    ------
    FileNotFoundError
        If the specified directory does not exist or if a filename cannot be found within it.

    """
    # Precondition: Directory exists
    if not os.path.isdir(dirpath):
        message = "Directory could not be found.\nGiven path: {}".format(dirpath)
        raise FileNotFoundError(message)

    # Find filepaths
    filepaths = []
    for fn in filenames:
        pattern = os.path.join(dirpath, "**", "{}".format(fn))
        found_filepaths = glob.glob(pattern, recursive=True)
        if len(found_filepaths) == 0:
            message = (
                "Filename could not be found in the given directory and its subdirectories."
                "\nGiven directory: {}\nGiven filename: {}.".format(dirpath, fn)
            )
            raise FileNotFoundError(message)
        chosen_filepath = found_filepaths[0]
        filepaths.append(chosen_filepath)
    return filepaths


def load_json_file(filepath: str) -> Any:
    """Load and return the content of a JSON file.

    Parameters
    ----------
    filepath : str
        The path to the JSON file.

    Returns
    -------
    data : Any
        The content of the JSON file, deserialized as Python objects.

    Raises
    ------
    FileNotFoundError
        If the JSON file does not exist.
    ValueError
        If the JSON file can not be loaded due to invalid content.

    """
    # Precondition: JSON file exists
    if not os.path.isfile(filepath):
        message = "JSON file could not be found.\nGiven path: {}".format(filepath)
        raise FileNotFoundError(message)

    # Load data
    try:
        with open(filepath) as f:
            return json.load(f)
    except Exception:
        message = (
            "JSON file could not be loaded. "
            "The content seems not to be in a valid format.\nGiven path: {}".format(
                filepath
            )
        )
        raise ValueError(message)
