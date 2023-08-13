import datetime
import hashlib
import html
from typing import Any, Dict


def transform_swae_data(
    swae_data: Dict[str, Any], filters_on: bool = False
) -> Dict[str, Any]:
    """Transform semi-structured JSON data from Swae into structured tabular data.

    Parameters
    ----------
    swae_data : Dict[str, Any]
        A dictionary containing the semi-structured data from Swae.

    filters_on : bool, optional
        Flag indicating whether filters are enabled for the transformation, by default False.

    Returns
    -------
    tabular_data : Dict[str, Any]
        A dictionary containing the transformed tabular data.

    Raises
    ------
    ValueError
        If there are errors in the data transformation process.

    """
    # Combine reactions (emojis), upvotes (thumbs up) and downvotes (thumbs down) into one reaction entity
    r1, c1, d1 = transform_reactions(swae_data["reactions"], filters_on)
    r2, c2, d2 = transform_upvotes(swae_data["upvotes"], filters_on)
    r3, c3, d3 = transform_downvotes(swae_data["downvotes"], filters_on)
    reactions_rows = r1 + r2 + r3
    reactions_cols = c1
    reactions_dtypes = d1

    # Transform all entities
    tabular_data = {
        "users": transform_users(swae_data["users"], filters_on),
        "missions": transform_missions(swae_data["missions"], filters_on),
        "proposals": transform_proposals(swae_data["proposals"], filters_on),
        "ratings": transform_ratings(swae_data["ratings"], filters_on),
        "comments": transform_comments(swae_data["comments"], filters_on),
        "reactions": (reactions_rows, reactions_cols, reactions_dtypes),
        "views": transform_views(swae_data["views"], filters_on),
    }
    return tabular_data


def transform_missions(missions_json, filters_on):
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
            deleted = conv_str(mission.get("deleted"))
            public = conv_bool(mission.get("publicChallenge"))
            state = conv_str(mission.get("state"))
            if deleted or not public or state != "Created":
                num_skipped += 1
                continue

        # Transformation
        row = [
            # Identifiers
            conv_str(mission.get("challengeId")),
            conv_str(mission.get("createdBy")),
            # Main attributes
            conv_str(mission.get("title")),
            conv_web_str(mission.get("description")),
            # Dates
            conv_timestamp(mission.get("createdAt")),
            conv_datetime(mission.get("createdAt")),
            conv_timestamp(mission.get("startDate")),
            conv_datetime(mission.get("startDate")),
            conv_timestamp(mission.get("expiryDate")),
            conv_datetime(mission.get("expiryDate")),
            # Counts
            conv_int(mission.get("totalUniqueViewCount")),
        ]
        rows.append(row)
    check_integrity(columns, datatypes, rows, missions_json, num_skipped)
    return rows, columns, datatypes


def transform_proposals(proposals_json, filters_on):
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
            deleted = conv_bool(proposal.get("deleted"))
            state = conv_str(proposal.get("state"))
            if deleted or state == "Draft":  # TODO: unclear if category "Draft" exists
                num_skipped += 1
                continue

        # Transformation
        row = [
            # Identifiers
            conv_str(proposal.get("documentId")),
            conv_str(proposal.get("challengeId")),
            conv_str(proposal.get("createdBy")),
            # Main attributes
            conv_str(proposal.get("title")),
            conv_web_str(proposal.get("summary")),
            conv_str(proposal.get("state")),
            conv_bool(proposal.get("isAnonymous")),
            conv_proposal_is_rejected(proposal.get("rejectedBy")),
            conv_int(proposal.get("timeSpentCreate")),
            conv_proposal_ratings(proposal.get("votesArr")),
            conv_float(proposal.get("averageVoteRating")),
            # Dates
            conv_timestamp(proposal.get("createdAt")),
            conv_datetime(proposal.get("createdAt")),
            conv_timestamp(proposal.get("publishedAt")),
            conv_datetime(proposal.get("publishedAt")),
            # Counts
            conv_proposal_num_files(proposal.get("files")),
            conv_int(proposal.get("totalUniqueViewCount")),
            conv_int(proposal.get("totalEngagementCount")),
            conv_int(proposal.get("ContributionTotalCount")),
            conv_int(proposal.get("ContributionUniqueCount")),
            conv_int(proposal.get("totalVoteCount")),
            conv_int(proposal.get("totalCommentCount")),
            conv_int(proposal.get("totalNeutralCommentCount")),
            conv_int(proposal.get("totalPositiveCommentCount")),
            conv_int(proposal.get("totalNegativeCommentCount")),
            conv_int(proposal.get("totalInlineCommentCount")),
            conv_int(proposal.get("totalSuggestionCount")),
            conv_int(proposal.get("totalInlineSuggestionCount")),
            conv_int(proposal.get("totalVolunteerCount")),
        ]
        rows.append(row)
    check_integrity(columns, datatypes, rows, proposals_json, num_skipped)
    return rows, columns, datatypes


def transform_users(users_json, filters_on):
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
            deleted = conv_bool(user.get("deleted"))
            if deleted:
                num_skipped += 1
                continue

        # Transformation
        row = [
            # Identifiers
            conv_str(user.get("userName")),
            # Main attributes
            conv_user_name(user.get("firstName"), user.get("lastName")),
            conv_user_email_address(user.get("userName")),
            conv_user_ethereum_address(user.get("userName")),
            conv_str(user.get("additionalWalletAddress")),
            conv_str(user.get("web3Nonce")),
            # Further attributes
            conv_str(user.get("myHandle")),
            conv_str(user.get("myBio")),
            conv_str(user.get("timeZone")),
            conv_str(user.get("age")),
            conv_str(user.get("gender")),
            conv_str(user.get("linkedInLink")),
            conv_str(user.get("mediumLink")),
            conv_str(user.get("twitterLink")),
            conv_str(user.get("providerName")),
            conv_timestamp(user.get("lastSeenAt")),
            conv_str(user.get("lastSeenCity")),
            conv_bool(user.get("signStatus")),
            conv_bool(user.get("contributionStatus")),
            # Dates
            conv_timestamp(user.get("createdAt")),
            conv_datetime(user.get("createdAt")),
            # Counts
            conv_int(user.get("voteCount")),
        ]
        rows.append(row)
    check_integrity(columns, datatypes, rows, users_json, num_skipped)
    return rows, columns, datatypes


def transform_ratings(ratings_json, filters_on):
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
            conv_str(rating.get("voteId")),
            conv_str(rating.get("documentId")),
            conv_str(rating.get("userName")),
            # Main attributes
            conv_float(rating.get("rating")),
            conv_bool(rating.get("isAnonymous")),
            conv_bool(rating.get("enable")),
            # Dates
            conv_timestamp(rating.get("createdAt")),
            conv_datetime(rating.get("createdAt")),
        ]
        rows.append(row)
    check_integrity(columns, datatypes, rows, ratings_json)
    return rows, columns, datatypes


def transform_comments(comments_json, filters_on):
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
            deleted = conv_bool(comment.get("deleted"))
            if deleted:
                num_skipped += 1
                continue

        # Transformation
        row = [
            # Identifiers
            conv_str(comment.get("commentId")),
            conv_str(comment.get("documentId")),
            conv_str(comment.get("createdBy")),
            conv_str(comment.get("parentCommentId")),
            # Main attributes
            conv_web_str(comment.get("commentText")),
            conv_str(comment.get("commentEmotion")),
            conv_int(comment.get("commentLevel")),
            conv_int(comment.get("timeSpent")),
            conv_bool(comment.get("isAnonymous")),
            conv_bool(comment.get("flagged")),
            # Dates
            conv_timestamp(comment.get("createdAt")),
            conv_datetime(comment.get("createdAt")),
            # Counts
            conv_int(comment.get("totalReplyCount")),
            conv_int(comment.get("endorseUpCount")),
            conv_int(comment.get("endorseDownCount")),
            conv_int(comment.get("angerCount")),
            conv_int(comment.get("celebrateCount")),
            conv_int(comment.get("clapCount")),
            conv_int(comment.get("curiousCount")),
            conv_int(comment.get("geniusCount")),
            conv_int(comment.get("happyCount")),
            conv_int(comment.get("hotCount")),
            conv_int(comment.get("laughCount")),
            conv_int(comment.get("loveCount")),
            conv_int(comment.get("sadCount")),
        ]
        rows.append(row)
    check_integrity(columns, datatypes, rows, comments_json, num_skipped)
    return rows, columns, datatypes


def transform_reactions(reactions_json, filters_on):
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
            create_unique_id(
                reaction.get("commentId"),
                reaction.get("userName"),
                reaction.get("reactionType"),
                reaction.get("createdAt"),
            ),
            conv_str(reaction.get("commentId")),
            conv_str(reaction.get("userName")),
            # Main attributes
            conv_str(reaction.get("reactionType")),
            # Dates
            conv_timestamp(reaction.get("createdAt")),
            conv_datetime(reaction.get("createdAt")),
        ]
        rows.append(row)
    check_integrity(columns, datatypes, rows, reactions_json)
    return rows, columns, datatypes


def transform_upvotes(upvotes_json, filters_on):
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
            create_unique_id(
                upvote.get("commentId"),
                upvote.get("userName"),
                upvote.get("reactionType"),
                upvote.get("createdAt"),
            ),
            conv_str(upvote.get("commentId")),
            conv_str(upvote.get("userName")),
            # Main attributes
            "upvote",
            # Dates
            conv_timestamp(upvote.get("createdAt")),
            conv_datetime(upvote.get("createdAt")),
        ]
        rows.append(row)
    check_integrity(columns, datatypes, rows, upvotes_json)
    return rows, columns, datatypes


def transform_downvotes(downvotes_json, filters_on):
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
            create_unique_id(
                downvote.get("commentId"),
                downvote.get("userName"),
                downvote.get("reactionType"),
                downvote.get("createdAt"),
            ),
            conv_str(downvote.get("commentId")),
            conv_str(downvote.get("userName")),
            # Main attributes
            "downvote",
            # Dates
            conv_timestamp(downvote.get("createdAt")),
            conv_datetime(downvote.get("createdAt")),
        ]
        rows.append(row)
    check_integrity(columns, datatypes, rows, downvotes_json)
    return rows, columns, datatypes


def transform_views(views_json, filters_on):
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
            create_unique_id(
                view.get("id"),
                view.get("userName"),
            ),
            conv_str(view.get("id")),
            conv_str(view.get("userName")),
        ]
        rows.append(row)
    check_integrity(columns, datatypes, rows, views_json)
    return rows, columns, datatypes


def check_integrity(columns, datatypes, rows, data_json, num_skipped=0):
    num_columns = len(columns)
    num_datatypes = len(datatypes)
    num_rows = len(rows)
    num_entries = len(rows[0])
    num_records = len(data_json)
    if num_columns != num_datatypes:
        message = (
            "Number of columns is not equal to number of datatypes: {} != {}".format(
                num_columns, num_datatypes
            )
        )
        raise ValueError(message)
    if num_columns != num_entries:
        message = "Number of columns is not equal to number of entries in first row: {} != {}".format(
            num_columns, num_entries
        )
        raise ValueError(message)
    if num_rows + num_skipped != num_records:
        message = "Number of rows (+ skipped rows) in the transformed data is not equal to number of records in the raw data: {}+{} != {}".format(
            num_rows, num_skipped, num_records
        )
        raise ValueError(message)


# Functions for converting individual attributes


def create_unique_id(*args):
    string = "|".join(str(a) for a in args)
    bytes_obj = string.encode("utf-8")
    hash_obj = hashlib.sha256(bytes_obj)
    new_string = hash_obj.hexdigest()
    return new_string


def get_val(item):
    val = list(item.values())[0]
    return val


def conv_str(item):
    try:
        result = str(get_val(item)).strip()
    except Exception:
        # Default
        result = ""
    return result


def conv_web_str(item):
    try:
        result = str(get_val(item))

        # Remove paragraph tags
        result = result.replace("</p>", "").replace("<p>", "\n").strip()

        # Convert escape sequences
        result = html.unescape(result)
    except Exception:
        # Default
        result = ""
    return result


def conv_int(item):
    try:
        result = int(get_val(item))
    except Exception:
        # Default
        result = 0
    return result


def conv_float(item):
    try:
        result = float(get_val(item))
    except Exception:
        # Default
        result = 0.0
    return result


def conv_bool(item):
    try:
        result = bool(get_val(item))
    except Exception:
        # Default
        result = False
    return result


def conv_timestamp(item):
    try:
        result = int(get_val(item))
    except Exception:
        # Default
        result = 0
    return result


def conv_datetime(item):
    try:
        result = int(get_val(item))
        dt = datetime.datetime.fromtimestamp(result / 1000.0)
        result = dt.isoformat(sep=" ", timespec="milliseconds")
    except Exception:
        # Default
        result = ""
    return result


def conv_proposal_ratings(item):
    try:
        value_counts = get_val(item)
        result = []
        for val, cnt in value_counts.items():
            if cnt is not None and val is not None:
                val = int(val)
                cnt = int(get_val(cnt))
                values = [val] * cnt
                result.extend(values)
        result.sort()
        result = str(result)
    except Exception:
        # Default
        result = []
        result = str(result)
    return result


def conv_proposal_is_rejected(item):
    try:
        result = bool(str(get_val(item)) != "")
    except Exception:
        # Default
        result = False
    return result


def conv_proposal_num_files(item):
    try:
        result = len(get_val(item))
    except Exception:
        # Default
        result = 0
    return result


def conv_user_name(first_name, last_name):
    try:
        first_name = str(get_val(first_name))
    except Exception:
        # Default first name
        first_name = ""
    try:
        last_name = str(get_val(last_name))
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


def conv_user_email_address(item):
    try:
        user_name = str(get_val(item))
        if "@" in user_name:
            email_address = user_name
        else:
            email_address = ""
    except Exception:
        # Default
        email_address = ""
    return email_address


def conv_user_ethereum_address(item):
    try:
        user_name = str(get_val(item))
        if "@" not in user_name:
            ethereum_address = user_name
        else:
            ethereum_address = ""
    except Exception:
        # Default
        ethereum_address = ""
    return ethereum_address
