-- Create a view for selected missions
CREATE VIEW filter{filter_id}_missions AS
    SELECT *
    FROM missions
    WHERE mission_id IN (
        {mission_ids}
    );

-- Create a view for selected proposals
CREATE VIEW filter{filter_id}_proposals AS
    SELECT *
    FROM proposals
    WHERE mission_id IN (
        {mission_ids}
    )
    AND (
        {timerange_conditions}
    );

-- Create a view for selected ratings
CREATE VIEW filter{filter_id}_ratings AS
    SELECT *
    FROM ratings
    WHERE proposal_id IN (
        SELECT proposal_id FROM filter{filter_id}_proposals
    )
    AND (
        {timerange_conditions}
    );

-- Create a view for selected comments
CREATE VIEW filter{filter_id}_comments AS
    SELECT *
    FROM comments
    WHERE proposal_id IN (
        SELECT proposal_id FROM filter{filter_id}_proposals
    )
    AND (
        {timerange_conditions}
    );

-- Create a view for selected reactions
CREATE VIEW filter{filter_id}_reactions AS
    SELECT *
    FROM reactions
    WHERE comment_id IN (
        SELECT comment_id FROM filter{filter_id}_comments
    )
    AND (
        {timerange_conditions}
    );