"""Module for transforming JSON data from Swae to structured tabular data."""

import datetime
import hashlib
import html
from typing import Any, Dict, List, Tuple, Union


def transform_swae_data(
    swae_data: Dict[str, Any], filters_on: bool = True
) -> Dict[str, Tuple]:
    """Transform semi-structured JSON data from Swae into structured tabular data.

    Parameters
    ----------
    swae_data : Dict[str, Any]
        A dictionary containing the semi-structured data extracted from a Swae export.
    filters_on : bool, optional, default=True
        A flag that determines whether filters are enabled for the transformation.
        If True, individual rows can be skipped if they carry an attribute that indicates that
        they are inactive, e.g. a proposal being in draft status or a comment being deleted.

    Returns
    -------
    tabular_data : Dict[str, Tuple]
        A dictionary containing the transformed tabular data.

    Raises
    ------
    ValueError
        If there are errors in the data transformation process.

    """
    # Combine reactions (emojis), upvotes (thumbs up) and downvotes (thumbs down)
    # into one reaction entity
    r1, c1, d1 = _transform_reactions(swae_data["reactions"], filters_on)
    r2, c2, d2 = _transform_upvotes(swae_data["upvotes"], filters_on)
    r3, c3, d3 = _transform_downvotes(swae_data["downvotes"], filters_on)
    reactions_rows = r1 + r2 + r3
    reactions_cols = c1
    reactions_dtypes = d1
    transformed_reactions = (reactions_rows, reactions_cols, reactions_dtypes)

    # Transform all entities
    tabular_data = {
        "users": _transform_users(swae_data["users"], filters_on),
        "missions": _transform_missions(swae_data["missions"], filters_on),
        "proposals": _transform_proposals(swae_data["proposals"], filters_on),
        "ratings": _transform_ratings(swae_data["ratings"], filters_on),
        "comments": _transform_comments(swae_data["comments"], filters_on),
        "reactions": transformed_reactions,
        "views": _transform_views(swae_data["views"], filters_on),
    }
    return tabular_data


def _transform_missions(
    missions_json: List[Dict], filters_on: bool
) -> Tuple[List, List, List]:
    columns = [
        # Identifiers
        "mission_id",
        "user_id",
        # Main attributes
        "title",
        "description",
        # Dates
        "creation_timestamp",
        "creation_datetime",
        "start_timestamp",
        "start_datetime",
        "end_timestamp",
        "end_datetime",
        # Counts
        "num_total_unique_views",
    ]

    datatypes = [
        # Identifiers
        "str",
        "str",
        # Main attributes
        "str",
        "str",
        # Dates
        "int",
        "str",
        "int",
        "str",
        "int",
        "str",
        # Counts
        "int",
    ]

    rows = []
    num_skipped = 0
    for mission in missions_json:
        # Skip missions that are not created, not public or deleted
        if filters_on:
            deleted = _conv_bool(mission.get("deleted"))
            public = _conv_bool(mission.get("publicChallenge"))
            state = _conv_str(mission.get("state"))
            if deleted or (not public) or (state != "Created"):
                num_skipped += 1
                continue

        # Transformation
        row = [
            # Identifiers
            _conv_str(mission.get("challengeId")),
            _conv_str(mission.get("createdBy")),
            # Main attributes
            _conv_str(mission.get("title")),
            _conv_web_str(mission.get("description")),
            # Dates
            _conv_timestamp(mission.get("createdAt")),
            _conv_datetime(mission.get("createdAt")),
            _conv_timestamp(mission.get("startDate")),
            _conv_datetime(mission.get("startDate")),
            _conv_timestamp(mission.get("expiryDate")),
            _conv_datetime(mission.get("expiryDate")),
            # Counts
            _conv_int(mission.get("totalUniqueViewCount")),
        ]
        rows.append(row)
    _check_integrity(columns, datatypes, rows, missions_json, num_skipped)
    return rows, columns, datatypes


def _transform_proposals(
    proposals_json: List[Dict], filters_on: bool
) -> Tuple[List, List, List]:
    columns = [
        # Identifiers
        "proposal_id",
        "mission_id",
        "user_id",
        # Main attributes
        "title",
        "summary",
        "state",
        "is_anonymous",
        "is_rejected",
        "time_spent_create",
        "ratings",
        "average_rating",
        # Dates
        "creation_timestamp",
        "creation_datetime",
        "publishing_timestamp",
        "publishing_datetime",
        # Counts
        "num_files",
        "num_total_unique_views",
        "num_total_engagements",
        "num_total_contributions",
        "num_unique_contributions",
        "num_total_ratings",
        "num_total_comments",
        "num_total_neutral_comments",
        "num_total_positive_comments",
        "num_total_negative_comments",
        "num_total_inline_comments",
        "num_total_suggestions",
        "num_total_inline_suggestions",
        "num_volunteers",
    ]

    datatypes = [
        # Identifiers
        "str",
        "str",
        "str",
        # Main attributes
        "str",
        "str",
        "str",
        "bool",
        "bool",
        "int",
        "str",
        "float",
        # Dates
        "int",
        "str",
        "int",
        "str",
        # Counts
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
    ]

    rows = []
    num_skipped = 0
    for proposal in proposals_json:
        # Skip proposals that are drafts or deleted
        if filters_on:
            deleted = _conv_bool(proposal.get("deleted"))
            state = _conv_str(proposal.get("state"))
            if deleted or (state == "Draft"):  # Unclear if that category exists
                num_skipped += 1
                continue

        # Transformation
        row = [
            # Identifiers
            _conv_str(proposal.get("documentId")),
            _conv_str(proposal.get("challengeId")),
            _conv_str(proposal.get("createdBy")),
            # Main attributes
            _conv_str(proposal.get("title")),
            _conv_web_str(proposal.get("summary")),
            _conv_str(proposal.get("state")),
            _conv_bool(proposal.get("isAnonymous")),
            _conv_proposal_is_rejected(proposal.get("rejectedBy")),
            _conv_int(proposal.get("timeSpentCreate")),
            _conv_proposal_ratings(proposal.get("votesArr")),
            _conv_float(proposal.get("averageVoteRating")),
            # Dates
            _conv_timestamp(proposal.get("createdAt")),
            _conv_datetime(proposal.get("createdAt")),
            _conv_timestamp(proposal.get("publishedAt")),
            _conv_datetime(proposal.get("publishedAt")),
            # Counts
            _conv_proposal_num_files(proposal.get("files")),
            _conv_int(proposal.get("totalUniqueViewCount")),
            _conv_int(proposal.get("totalEngagementCount")),
            _conv_int(proposal.get("ContributionTotalCount")),
            _conv_int(proposal.get("ContributionUniqueCount")),
            _conv_int(proposal.get("totalVoteCount")),
            _conv_int(proposal.get("totalCommentCount")),
            _conv_int(proposal.get("totalNeutralCommentCount")),
            _conv_int(proposal.get("totalPositiveCommentCount")),
            _conv_int(proposal.get("totalNegativeCommentCount")),
            _conv_int(proposal.get("totalInlineCommentCount")),
            _conv_int(proposal.get("totalSuggestionCount")),
            _conv_int(proposal.get("totalInlineSuggestionCount")),
            _conv_int(proposal.get("totalVolunteerCount")),
        ]
        rows.append(row)
    _check_integrity(columns, datatypes, rows, proposals_json, num_skipped)
    return rows, columns, datatypes


def _transform_users(
    users_json: List[Dict], filters_on: bool
) -> Tuple[List, List, List]:
    columns = [
        # Identifiers
        "user_id",
        # Main attributes
        "name",
        "email_address",
        "ethereum_address",
        "cardano_address",
        "web3_nonce",
        # Further attributes
        "handle",
        "bio",
        "timezone",
        "age_range",
        "gender",
        "linkedin_link",
        "medium_link",
        "twitter_link",
        "provider_name",
        "last_seen_time",
        "last_seen_location",
        "sign_status",
        "contribution_status",
        # Dates
        "creation_timestamp",
        "creation_datetime",
        # Counts
        "num_votes",
    ]

    datatypes = [
        # Identifiers
        "str",
        # Main attributes
        "str",
        "str",
        "str",
        "str",
        "str",
        # Further attributes
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "int",
        "str",
        "bool",
        "bool",
        # Dates
        "int",
        "str",
        # Counts
        "int",
    ]

    rows = []
    num_skipped = 0
    for user in users_json:
        # Skip users that are deleted
        if filters_on:
            deleted = _conv_bool(user.get("deleted"))
            if deleted:
                num_skipped += 1
                continue

        # Transformation
        row = [
            # Identifiers
            _conv_str(user.get("userName")),
            # Main attributes
            _conv_user_name(user.get("firstName"), user.get("lastName")),
            _conv_user_email_address(user.get("userName")),
            _conv_user_ethereum_address(user.get("userName")),
            _conv_str(user.get("additionalWalletAddress")),
            _conv_str(user.get("web3Nonce")),
            # Further attributes
            _conv_str(user.get("myHandle")),
            _conv_str(user.get("myBio")),
            _conv_str(user.get("timeZone")),
            _conv_str(user.get("age")),
            _conv_str(user.get("gender")),
            _conv_str(user.get("linkedInLink")),
            _conv_str(user.get("mediumLink")),
            _conv_str(user.get("twitterLink")),
            _conv_str(user.get("providerName")),
            _conv_timestamp(user.get("lastSeenAt")),
            _conv_str(user.get("lastSeenCity")),
            _conv_bool(user.get("signStatus")),
            _conv_bool(user.get("contributionStatus")),
            # Dates
            _conv_timestamp(user.get("createdAt")),
            _conv_datetime(user.get("createdAt")),
            # Counts
            _conv_int(user.get("voteCount")),
        ]
        rows.append(row)
    _check_integrity(columns, datatypes, rows, users_json, num_skipped)
    return rows, columns, datatypes


def _transform_ratings(
    ratings_json: List[Dict], filters_on: bool
) -> Tuple[List, List, List]:
    columns = [
        # Identifiers
        "rating_id",
        "proposal_id",
        "user_id",
        # Main attributes
        "rating",
        "is_anonymous",
        "enable",
        # Dates
        "creation_timestamp",
        "creation_datetime",
    ]

    datatypes = [
        # Identifiers
        "str",
        "str",
        "str",
        # Main attributes
        "int",
        "bool",
        "bool",
        # Dates
        "int",
        "str",
    ]

    rows = []
    for rating in ratings_json:
        row = [
            # Identifiers
            _conv_str(rating.get("voteId")),
            _conv_str(rating.get("documentId")),
            _conv_str(rating.get("userName")),
            # Main attributes
            _conv_float(rating.get("rating")),
            _conv_bool(rating.get("isAnonymous")),
            _conv_bool(rating.get("enable")),
            # Dates
            _conv_timestamp(rating.get("createdAt")),
            _conv_datetime(rating.get("createdAt")),
        ]
        rows.append(row)
    _check_integrity(columns, datatypes, rows, ratings_json)
    return rows, columns, datatypes


def _transform_comments(
    comments_json: List[Dict], filters_on: bool
) -> Tuple[List, List, List]:
    columns = [
        # Identifiers
        "comment_id",
        "proposal_id",
        "user_id",
        "parent_comment_id",
        # Main attributes
        "text",
        "emotion",
        "level",
        "time_spent",
        "is_anonymous",
        "is_flagged",
        # Dates
        "creation_timestamp",
        "creation_datetime",
        # Counts
        "num_total_replies",
        "num_endorse_up_reactions",
        "num_endorse_down_reactions",
        "num_anger_reactions",
        "num_celebrate_reactions",
        "num_clap_reactions",
        "num_curious_reactions",
        "num_genius_reactions",
        "num_happy_reactions",
        "num_hot_reactions",
        "num_laugh_reactions",
        "num_love_reactions",
        "num_sad_reactions",
    ]

    datatypes = [
        # Identifiers
        "str",
        "str",
        "str",
        "str",
        # Main attributes
        "str",
        "str",
        "int",
        "int",
        "bool",
        "bool",
        # Dates
        "int",
        "str",
        # Counts
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
        "int",
    ]

    rows = []
    num_skipped = 0
    for comment in comments_json:
        # Skip comments that are deleted
        if filters_on:
            deleted = _conv_bool(comment.get("deleted"))
            if deleted:
                num_skipped += 1
                continue

        # Transformation
        row = [
            # Identifiers
            _conv_str(comment.get("commentId")),
            _conv_str(comment.get("documentId")),
            _conv_str(comment.get("createdBy")),
            _conv_str(comment.get("parentCommentId")),
            # Main attributes
            _conv_web_str(comment.get("commentText")),
            _conv_str(comment.get("commentEmotion")),
            _conv_int(comment.get("commentLevel")),
            _conv_int(comment.get("timeSpent")),
            _conv_bool(comment.get("isAnonymous")),
            _conv_bool(comment.get("flagged")),
            # Dates
            _conv_timestamp(comment.get("createdAt")),
            _conv_datetime(comment.get("createdAt")),
            # Counts
            _conv_int(comment.get("totalReplyCount")),
            _conv_int(comment.get("endorseUpCount")),
            _conv_int(comment.get("endorseDownCount")),
            _conv_int(comment.get("angerCount")),
            _conv_int(comment.get("celebrateCount")),
            _conv_int(comment.get("clapCount")),
            _conv_int(comment.get("curiousCount")),
            _conv_int(comment.get("geniusCount")),
            _conv_int(comment.get("happyCount")),
            _conv_int(comment.get("hotCount")),
            _conv_int(comment.get("laughCount")),
            _conv_int(comment.get("loveCount")),
            _conv_int(comment.get("sadCount")),
        ]
        rows.append(row)
    _check_integrity(columns, datatypes, rows, comments_json, num_skipped)
    return rows, columns, datatypes


def _transform_reactions(
    reactions_json: List[Dict], filters_on: bool
) -> Tuple[List, List, List]:
    columns = [
        # Identifiers
        "reaction_id",
        "comment_id",
        "user_id",
        # Main attributes
        "reaction_type",
        # Dates
        "creation_timestamp",
        "creation_datetime",
    ]

    datatypes = [
        # Identifiers
        "str",
        "str",
        "str",
        # Main attributes
        "str",
        # Dates
        "int",
        "str",
    ]

    rows = []
    for reaction in reactions_json:
        row = [
            # Identifiers
            _create_unique_id(
                reaction.get("commentId"),
                reaction.get("userName"),
                reaction.get("reactionType"),
                reaction.get("createdAt"),
            ),
            _conv_str(reaction.get("commentId")),
            _conv_str(reaction.get("userName")),
            # Main attributes
            _conv_str(reaction.get("reactionType")),
            # Dates
            _conv_timestamp(reaction.get("createdAt")),
            _conv_datetime(reaction.get("createdAt")),
        ]
        rows.append(row)
    _check_integrity(columns, datatypes, rows, reactions_json)
    return rows, columns, datatypes


def _transform_upvotes(
    upvotes_json: List[Dict], filters_on: bool
) -> Tuple[List, List, List]:
    columns = [
        # Identifiers
        "reaction_id",
        "comment_id",
        "user_id",
        # Main attributes
        "reaction_type",
        # Dates
        "creation_timestamp",
        "creation_datetime",
    ]

    datatypes = [
        # Identifiers
        "str",
        "str",
        "str",
        # Main attributes
        "str",
        # Dates
        "int",
        "str",
    ]

    rows = []
    for upvote in upvotes_json:
        row = [
            # Identifiers
            _create_unique_id(
                upvote.get("commentId"),
                upvote.get("userName"),
                upvote.get("reactionType"),
                upvote.get("createdAt"),
            ),
            _conv_str(upvote.get("commentId")),
            _conv_str(upvote.get("userName")),
            # Main attributes
            "upvote",
            # Dates
            _conv_timestamp(upvote.get("createdAt")),
            _conv_datetime(upvote.get("createdAt")),
        ]
        rows.append(row)
    _check_integrity(columns, datatypes, rows, upvotes_json)
    return rows, columns, datatypes


def _transform_downvotes(
    downvotes_json: List[Dict], filters_on: bool
) -> Tuple[List, List, List]:
    columns = [
        # Identifiers
        "reaction_id",
        "comment_id",
        "user_id",
        # Main attributes
        "reaction_type",
        # Dates
        "creation_timestamp",
        "creation_datetime",
    ]

    datatypes = [
        # Identifiers
        "str",
        "str",
        "str",
        # Main attributes
        "str",
        # Dates
        "int",
        "str",
    ]

    rows = []
    for downvote in downvotes_json:
        row = [
            # Identifiers
            _create_unique_id(
                downvote.get("commentId"),
                downvote.get("userName"),
                downvote.get("reactionType"),
                downvote.get("createdAt"),
            ),
            _conv_str(downvote.get("commentId")),
            _conv_str(downvote.get("userName")),
            # Main attributes
            "downvote",
            # Dates
            _conv_timestamp(downvote.get("createdAt")),
            _conv_datetime(downvote.get("createdAt")),
        ]
        rows.append(row)
    _check_integrity(columns, datatypes, rows, downvotes_json)
    return rows, columns, datatypes


def _transform_views(
    views_json: List[Dict], filters_on: bool
) -> Tuple[List, List, List]:
    columns = [
        # Identifiers
        "view_id",
        "proposal_id",
        "user_id",
    ]

    datatypes = [
        # Identifiers
        "str",
        "str",
        "str",
    ]

    rows = []
    for view in views_json:
        row = [
            _create_unique_id(
                view.get("id"),
                view.get("userName"),
            ),
            _conv_str(view.get("id")),
            _conv_str(view.get("userName")),
        ]
        rows.append(row)
    _check_integrity(columns, datatypes, rows, views_json)
    return rows, columns, datatypes


def _check_integrity(
    columns: List[str],
    datatypes: List[str],
    rows: List[List[Any]],
    data_json: List[Dict],
    num_skipped: int = 0,
) -> None:
    """Ensure that the result of a transformation fulfills some basic form criteria."""
    num_columns = len(columns)
    num_datatypes = len(datatypes)
    num_rows = len(rows)
    num_entries = len(rows[0])
    num_records = len(data_json)
    if num_columns != num_datatypes:
        message = (
            "Number of columns is not equal to "
            f"number of datatypes: {num_columns} != {num_datatypes}"
        )
        raise ValueError(message)
    if num_columns != num_entries:
        message = (
            "Number of columns is not equal to "
            f"number of entries in first row: {num_columns} != {num_entries}"
        )
        raise ValueError(message)
    if num_rows + num_skipped != num_records:
        message = (
            "Number of rows (+ skipped rows) in the transformed data is not equal to "
            f"number of records in the raw data: {num_rows}+{num_skipped} != {num_records}"
        )
        raise ValueError(message)


def _create_unique_id(*args: Any) -> str:
    """Create a unique identifier based on input arguments.

    This function takes a variable number of arguments, converts them to strings,
    and then generates a unique identifier by hashing the concatenated string using SHA-256.

    Parameters
    ----------
    *args : Any
        Variable number of arguments to be used in creating the unique ID.

    Returns
    -------
    unique_id : str
        An identifier that is unique for the provided arguments.

    """
    string = "|".join(str(a) for a in args)
    bytes_obj = string.encode("utf-8")
    hash_obj = hashlib.sha256(bytes_obj)
    new_string = hash_obj.hexdigest()
    return new_string


def _get_val(item: Dict) -> Any:
    val = list(item.values())[0]
    return val


def _conv_str(item: Union[dict, None]) -> str:
    try:
        result = str(_get_val(item)).strip()
    except Exception:
        # Default
        result = ""
    return result


def _conv_web_str(item: Union[dict, None]) -> str:
    try:
        result = str(_get_val(item))

        # Remove paragraph tags
        result = result.replace("</p>", "").replace("<p>", "\n").strip()

        # Convert escape sequences
        result = html.unescape(result)
    except Exception:
        # Default
        result = ""
    return result


def _conv_int(item: Union[dict, None]) -> int:
    try:
        result = int(_get_val(item))
    except Exception:
        # Default
        result = 0
    return result


def _conv_float(item: Union[dict, None]) -> float:
    try:
        result = float(_get_val(item))
    except Exception:
        # Default
        result = 0.0
    return result


def _conv_bool(item: Union[dict, None]) -> bool:
    try:
        result = bool(_get_val(item))
    except Exception:
        # Default
        result = False
    return result


def _conv_timestamp(item: Union[dict, None]) -> int:
    try:
        result = int(_get_val(item))
    except Exception:
        # Default
        result = 0
    return result


def _conv_datetime(item: Union[dict, None]) -> str:
    try:
        result = int(_get_val(item))
        dt = datetime.datetime.fromtimestamp(result / 1000.0)
        result = dt.isoformat(sep=" ", timespec="milliseconds")
    except Exception:
        # Default
        result = ""
    return result


def _conv_proposal_ratings(item: Union[dict, None]) -> str:
    try:
        value_counts = _get_val(item)
        result = []
        for val, cnt in value_counts.items():
            if cnt is not None and val is not None:
                val = int(val)
                cnt = int(_get_val(cnt))
                values = [val] * cnt
                result.extend(values)
        result.sort()
        result = str(result)
    except Exception:
        # Default
        result = []
        result = str(result)
    return result


def _conv_proposal_is_rejected(item: Union[dict, None]) -> bool:
    try:
        result = bool(str(_get_val(item)) != "")
    except Exception:
        # Default
        result = False
    return result


def _conv_proposal_num_files(item: Union[dict, None]) -> int:
    try:
        result = len(_get_val(item))
    except Exception:
        # Default
        result = 0
    return result


def _conv_user_name(first_name: Union[dict, None], last_name: Union[dict, None]) -> str:
    try:
        first_name = str(_get_val(first_name))
    except Exception:
        # Default first name
        first_name = ""
    try:
        last_name = str(_get_val(last_name))
    except Exception:
        # Default last name
        last_name = ""

    if first_name and last_name:
        name = first_name + " " + last_name
    elif first_name:
        name = first_name
    elif last_name:
        name = last_name
    else:
        # Default
        name = ""
    return name


def _conv_user_email_address(item: Union[dict, None]) -> str:
    try:
        user_name = str(_get_val(item))
        if "@" in user_name:
            email_address = user_name
        else:
            email_address = ""
    except Exception:
        # Default
        email_address = ""
    return email_address


def _conv_user_ethereum_address(item: Union[dict, None]) -> str:
    try:
        user_name = str(_get_val(item))
        if "@" not in user_name:
            ethereum_address = user_name
        else:
            ethereum_address = ""
    except Exception:
        # Default
        ethereum_address = ""
    return ethereum_address
