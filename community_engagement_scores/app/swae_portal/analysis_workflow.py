import base64
import os
import sqlite3
import zipfile

from ccs import swae_analysis as swa

from django.conf import settings


class Workflow:
    def __init__(self, request):
        self.state = SessionState(request)

    def upload_file(self, file_obj):
        # Get
        filename = file_obj.name
        dirpath = self.state.dirpath

        # Convert
        filepath = os.path.join(dirpath, filename)
        with open(filepath, 'wb+') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        # Set
        self.state.zip_filename = filename
        self.state.zip_filepath = filepath

    def convert_zip_to_sqlite(self):
        # Get
        zip_filepath = self.state.zip_filepath
        dirpath = self.state.dirpath

        # Convert
        sqlite_filename = "ccs.sqlite"
        sqlite_filepath = os.path.join(dirpath, sqlite_filename)
        con = swa.zip_to_sqlite(zip_filepath, sqlite_filepath)
        con.close()

        # Set
        self.state.sqlite_filename = sqlite_filename
        self.state.sqlite_filepath = sqlite_filepath
        con.close()

    def convert_sqlite_to_excel(self):
        # Get
        sqlite_filepath = self.state.sqlite_filepath
        dirpath = self.state.dirpath

        # Convert
        excel_filename = "ccs.xlsx"
        excel_filepath = os.path.join(dirpath, excel_filename)
        con = sqlite3.connect(sqlite_filepath)
        swa.sqlite_to_excel(con, excel_filepath)
        con.close()

        # Set
        self.state.excel_filename = excel_filename
        self.state.excel_filepath = excel_filepath

    def filter_missions(self, selected_mission_ids):
        # Get
        sqlite_filepath = self.state.sqlite_filepath
        filter_id = self.state.filter_id
        filter_id = 1 if filter_id is None else filter_id+1

        # Convert
        con = sqlite3.connect(sqlite_filepath)
        swa.create_filter_views(con, filter_id, selected_mission_ids, extra_time_in_days=100)
        con.close()

        # Set
        self.state.filter_id = filter_id

    def calculate_scores(self, variables):
        # Get
        sqlite_filepath = self.state.sqlite_filepath
        filter_id = self.state.filter_id
        variables_id = self.state.variables_id
        variables_id = 1 if variables_id is None else variables_id+1

        # Convert
        con = sqlite3.connect(sqlite_filepath)
        swa.create_counts_table(
            con,
            filter_id,
        )
        swa.create_contribution_score_table(
            con,
            filter_id,
            variables_id,
            variables,
        )
        con.close()

        # Set
        self.state.score_variables = variables
        self.state.variables_id = variables_id

    def calculate_rewards(self, filtered_user_ids, function_agix_reward, function_voting_weight, threshold_percentile,
                          total_agix_reward, min_voting_weight, max_voting_weight):
        # Get
        sqlite_filepath = self.state.sqlite_filepath
        filter_id = self.state.filter_id
        variables_id = self.state.variables_id
        distribution_id = self.state.distribution_id
        distribution_id = 1 if distribution_id is None else distribution_id+1

        # Convert
        con = sqlite3.connect(sqlite_filepath)
        swa.create_rewards_table(
            con,
            filter_id,
            variables_id,
            distribution_id,
            filtered_user_ids,
            function_agix_reward,
            function_voting_weight,
            threshold_percentile,
            total_agix_reward,
            min_voting_weight,
            max_voting_weight,
        )
        con.close()

        # Set
        self.state.reward_variables = dict(
            num_filtered_user_ids=len(filtered_user_ids),
            function_agix_reward=function_agix_reward,
            function_voting_weight=function_voting_weight,
            threshold_percentile=threshold_percentile,
            total_agix_reward=total_agix_reward,
            min_voting_weight=min_voting_weight,
            max_voting_weight=max_voting_weight,
        )
        self.state.distribution_id = distribution_id

    def create_visualizations(self):
        # Get
        dirpath = self.state.dirpath
        sqlite_filepath = self.state.sqlite_filepath
        filter_id = self.state.filter_id
        variables_id = self.state.variables_id
        distribution_id = self.state.distribution_id

        file_format = 'png'
        filename_scores = f"contribution_scores.{file_format}"
        filename_agix = f"agix_rewards.{file_format}"
        filename_vw = f"voting_weights.{file_format}"

        # Convert
        filepath_scores = os.path.join(dirpath, filename_scores)
        filepath_agix = os.path.join(dirpath, filename_agix)
        filepath_vw = os.path.join(dirpath, filename_vw)
        con = sqlite3.connect(sqlite_filepath)
        fig1, fig2, fig3 = swa.visualize_rewards(con, filter_id, variables_id, distribution_id)
        fig1.savefig(filepath_scores, format=file_format)
        fig2.savefig(filepath_agix, format=file_format)
        fig3.savefig(filepath_vw, format=file_format)

        # Set
        self.state.fig_scores_filename = filename_scores
        self.state.fig_scores_filepath = filepath_scores
        self.state.fig_agix_filename = filename_agix
        self.state.fig_agix_filepath = filepath_agix
        self.state.fig_vw_filename = filename_vw
        self.state.fig_vw_filepath = filepath_vw

    def create_report(self):
        # Get
        dirpath = self.state.dirpath
        filepath_scores = self.state.fig_scores_filepath
        filepath_agix = self.state.fig_agix_filepath
        filepath_vw = self.state.fig_vw_filepath
        score_variables = self.state.score_variables
        reward_variables = self.state.reward_variables

        # Convert
        def image_to_base64(filepath):
            with open(filepath, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")

        scores_base64 = image_to_base64(filepath_scores)
        agix_base64 = image_to_base64(filepath_agix)
        vw_base64 = image_to_base64(filepath_vw)

        def clean_attribute(s):
            return ' '.join([x.capitalize() for x in s.split('_')])

        def to_table(data, skip_zero=False):
            header = '<tr><th>Variable</th><th>Value</th></tr>'
            content = '\n'.join([f'<tr><td>{clean_attribute(key)}</td><td>{val}</td></tr>'
                                 for key, val in data.items()
                                 if (not skip_zero or val != 0)])
            return '<table>' + header + content + '</table>'

        score_variables_html = to_table(score_variables, skip_zero=True)
        reward_variables_html = to_table(reward_variables)

        css_text = """
        html {
            background-color: black;
        }
        body {
            margin: 5% 15%;
            padding: 0;
            color: #dedce3;
            font-family: "Open Sans", sans-serif;
            font-size: 14px;
            letter-spacing: -0.1px;
            font-synthesis: none;
            -moz-font-feature-settings: "kern";
        }
        h1, h2, h3, h4, h5, h6 {
            text-transform: capitalize;
            margin-top: 1rem;
            margin-bottom: .5rem;
            margin-left: -1.5rem;
            font-weight: 500;
            line-height: 1.2;
            background: linear-gradient(225deg, #32c5ff 0%, #b620e0 52%, #f7b500 95%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        h1, h2, h3, h4 {
            font-family: "Inter", sans-serif;
            font-size: 48px;
            font-weight: 800;
            letter-spacing: -0.8px;
            line-height: 60px;
        }
        h2 {
            font-family: 'Roboto', sans-serif;
            font-size: 24px;
            font-weight: normal;
            color: #666;
            margin-bottom: 5px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px auto;
            table-layout: fixed;
        }
        th, td {
            padding: 6px;
            text-align: left;
            border-bottom: 1px solid #b620e0;
            background-color: black;
        }
        th {
            background-color: black;
            color: #b620e0;
        }
        tr:hover td {
            background-color: #b620e0;
        }
        .image-container {
            margin-bottom: 20px;
            width: 90%;
            display: flex;
            flex-direction: column;
            align-items: center;
            border-radius: 8px;
            background-color: white;
        }
        .image-container img {
            margin: 10px;
            width: 100%;
            max-width: 100%;
        }
"""

        html_text = f"""<html>
<head>
    <title>Report of community contribution score calculation</title>
    <style>{css_text}    </style>
</head>
<body>
    <h1>Figures</h1>
    <h2>Contribution scores</h2>
    <div class="image-container">
        <img src="data:image/png;base64,{scores_base64}" alt="Contribution scores Image">
    </div>
    <h2>Reward distribution</h2>
    <div class="image-container">
        <img src="data:image/png;base64,{agix_base64}" alt="AGIX rewards image">
    </div>
    <div class="image-container">
        <img src="data:image/png;base64,{vw_base64}" alt="Voting weights image">
    </div>
    <h1>Settings</h1>
    <h2>Contribution scores</h2>
    {score_variables_html}
    <h2>Reward distribution</h2>
    {reward_variables_html}
</body>
</html>"""

        filename = "report.html"
        filepath = os.path.join(dirpath, filename)
        with open(filepath, "w") as f:
            f.write(html_text)

        # Set
        self.state.report_filename = filename
        self.state.report_filepath = filepath

    def create_zip_file(self):
        # Get
        dirpath = self.state.dirpath
        filepaths = [
            self.state.zip_filepath,
            self.state.sqlite_filepath,
            self.state.excel_filepath,
            self.state.fig_scores_filepath,
            self.state.fig_agix_filepath,
            self.state.fig_vw_filepath,
            self.state.report_filepath,
        ]

        # Convert
        filename = "results.zip"
        filepath = os.path.join(dirpath, filename)
        with zipfile.ZipFile(filepath, 'w') as f:
            for filepath in filepaths:
                f.write(filepath, os.path.basename(filepath))

        # Set
        self.state.results_filename = filename
        self.state.results_filepath = filepath

    def get_mission_information(self):
        # Get
        sqlite_filepath = self.state.sqlite_filepath

        # Convert
        con = sqlite3.connect(sqlite_filepath)
        all_missions = swa.get_mission_information(con)
        con.close()

        # Return
        return all_missions

    def get_user_information(self):
        # Get
        sqlite_filepath = self.state.sqlite_filepath
        filter_id = self.state.filter_id

        # Convert
        con = sqlite3.connect(sqlite_filepath)
        user_information = swa.get_user_information(con, filter_id=filter_id)
        con.close()

        # Return
        return user_information


class SessionState:
    STATE_KEY = "swae_internal_session_data"

    def __init__(self, request):
        self.session = request.session
        if self.is_present_in_session():
            self.load()
        else:
            self.create()

    def __getattr__(self, name):
        if name in ("_session_data", "session"):
            return object.__getattribute__(self, name)
        else:
            return self._session_data.get(name, None)

    def __setattr__(self, name, value):
        if name in ("_session_data", "session"):
            self.__dict__[name] = value
        else:
            self._session_data[name] = value
            self.save()

    def __delattr__(self, name):
        if name in ("_session_data", "session"):
            del self.__dict__[name]
        elif name in self._session_data:
            del self._session_data[name]

    def __repr__(self):
        return repr(self._session_data)

    def is_present_in_session(self):
        return self.STATE_KEY in self.session

    def load(self):
        self._session_data = self.session[self.STATE_KEY]

    def create(self):
        if not self.session.session_key:
            self.session.save()
        session_key = self.session.session_key
        dirpath = self.create_tempdir(dirname=session_key)

        initial_state = {
            "session_key": session_key,
            "dirpath": dirpath,
        }
        self._session_data = self.session[self.STATE_KEY] = initial_state
        self.save()

    def reset(self):
        del self.session[self.STATE_KEY]
        del self._session_data
        self.save()

    def save(self):
        # Set session to modified to ensure a new state gets saved
        self.session.modified = True

    def create_tempdir(self, dirname):
        # Argument processing
        if not dirname or not isinstance(dirname, str):
            raise ValueError(f"Directory name is not a valid string: {dirname}")

        # Create directory
        dirpath = os.path.join(settings.BASE_DIR, settings.SWAE_TEMP_DIR, dirname)
        os.makedirs(dirpath, exist_ok=True)
        return dirpath