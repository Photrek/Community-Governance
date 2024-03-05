import os

from django import forms
from django.core.validators import FileExtensionValidator
from django.http import FileResponse, Http404, HttpResponseNotFound
from django.shortcuts import render
from django.views import View

from . import analysis_workflow as aw


# Views


class DataAnalysis(View):
    template_name = "data_analysis.html"

    def get(self, request):
        wf = aw.Workflow(request)

        upload_form = ZipFileUploadForm()
        context = {
            "step": 1,
            "upload_form": upload_form,
            "state": wf.state,
        }
        response = render(request, self.template_name, context)
        return response

    def post(self, request):
        if "upload_button" in request.POST:
            response = self.handle_upload_button(request)
        elif "filter_button" in request.POST:
            response = self.handle_filter_button(request)
        elif "calculate_scores_button" in request.POST:
            response = self.handle_calculate_scores_button(request)
        elif "calculate_rewards_button" in request.POST:
            response = self.handle_calculate_rewards_button(request)
        else:
            response = self.handle_default(request)
        return response

    def handle_upload_button(self, request):
        wf = aw.Workflow(request)

        error_message = "An unknown issue occurred. Sorry about that."
        try:
            # Parse form data
            try:
                upload_form = ZipFileUploadForm(request.POST, request.FILES)
                assert upload_form.is_valid()
                file_obj = upload_form.cleaned_data["select_button"]
            except Exception as e:
                error_message = (
                    "The provided file is not in a valid format. "
                    "Please provide a zip file."
                )
                raise e

            # Store zip file in session-specific temporary directory
            try:
                wf.upload_file(file_obj)
            except Exception as e:
                error_message = (
                    "The provided zip file could not be uploaded to the "
                    f"server: {repr_exception(e)}"
                )
                raise e

            # Convert the zip file to an SQLite file in the temporary directory
            try:
                wf.convert_zip_to_sqlite()
            except Exception as e:
                error_message = (
                    "The provided zip file could not be converted to a SQLite database. "
                    "Please ensure it is a valid export from the Swae portal."
                )
                raise e

            # Get available missions from the SQLite file to display them in the next form
            try:
                missions = wf.get_missions()
                assert len(missions) > 0
                filter_form = FilterForm(missions=missions)
            except Exception as e:
                error_message = (
                    "The provided zip file seems to contain not a "
                    f"single mission: {repr_exception(e)}"
                )
                raise e

            # Prepare data for successful step
            context = {
                "step": 2,
                "filter_form": filter_form,
                "state": wf.state,
            }
        except Exception:
            # Prepare data for failed step
            context = {
                "step": 1,
                "upload_form": upload_form,
                "upload_error_message": error_message,
                "state": wf.state,
            }

        response = render(request, self.template_name, context)
        return response

    def handle_filter_button(self, request):
        wf = aw.Workflow(request)

        error_message = "An unknown issue occurred. Sorry about that."
        try:
            # Parse form data
            try:
                missions = wf.get_missions()
                filter_form = FilterForm(request.POST, missions=missions)
                assert filter_form.is_valid()
                data = filter_form.cleaned_data
            except Exception as e:
                error_message = (
                    f"The submitted data contained an invalid item: {repr_exception(e)}"
                )
                raise e

            # Fetch selected missions
            try:
                selected_mission_ids = [
                    name
                    for name, val in data.items()
                    if val and name != "filter_button"
                ]
                assert len(selected_mission_ids) > 0
            except Exception as e:
                error_message = (
                    "The current selection contains zero missions. "
                    "Please select at least one mission."
                )
                raise e

            # Apply the mission filter
            try:
                wf.filter_missions(selected_mission_ids)
            except Exception as e:
                error_message = f"Filtering the missions failed: {repr_exception(e)}"
                raise e

            # Prepare data for successful step
            calculate_scores_form = CalculateScoresForm()
            context = {
                "step": 3,
                "calculate_scores_form": calculate_scores_form,
                "state": wf.state,
            }
        except Exception:
            # Prepare data for failed step
            context = {
                "step": 2,
                "filter_form": filter_form,
                "filter_error_message": error_message,
                "state": wf.state,
            }

        response = render(request, self.template_name, context)
        return response

    def handle_calculate_scores_button(self, request):
        wf = aw.Workflow(request)

        error_message = "An unknown issue occurred. Sorry about that."
        try:
            # Parse form data
            try:
                calculate_scores_form = CalculateScoresForm(request.POST)
                assert calculate_scores_form.is_valid()
                data = calculate_scores_form.cleaned_data
                variables = {
                    name: val
                    for name, val in data.items()
                    if name != "calculate_scores_button"
                }
            except Exception as e:
                error_message = (
                    f"The submitted data contained an invalid item: {repr_exception(e)}"
                )
                raise e

            # Calculate engagement scores and reward distribution
            try:
                wf.calculate_scores(variables)
            except Exception as e:
                error_message = (
                    f"Engagement score calculation failed: {repr_exception(e)}"
                )
                raise e

            # Fetch active users to display them as part of the next form
            try:
                users = wf.get_users()
                calculate_rewards_form = CalculateRewardsForm(users=users)
            except Exception as e:
                error_message = (
                    "Could not get information about users that were active in the "
                    f"selected missions: {repr_exception(e)}"
                )
                raise e

            # Prepare data for successful step
            context = {
                "step": 4,
                "calculate_rewards_form": calculate_rewards_form,
                "state": wf.state,
            }
        except Exception:
            # Prepare data for failed step
            context = {
                "step": 3,
                "calculate_scores_form": calculate_scores_form,
                "calculate_scores_error_message": error_message,
                "state": wf.state,
            }

        response = render(request, self.template_name, context)
        return response

    def handle_calculate_rewards_button(self, request):
        wf = aw.Workflow(request)

        error_message = "An unknown issue occurred. Sorry about that."
        try:
            # Parse form data
            try:
                users = wf.get_users()
                calculate_rewards_form = CalculateRewardsForm(request.POST, users=users)
                assert calculate_rewards_form.is_valid()
                data = calculate_rewards_form.cleaned_data
                filtered_user_ids = []
                for name, val in data.items():
                    if (
                        val is True
                        and name in calculate_rewards_form.field_groups[1]["fields"]
                    ):
                        filtered_user_ids.append(name)
                function_agix_reward = data["function_agix_reward"]
                function_voting_weight = data["function_voting_weight"]
                threshold_percentile = data["threshold_percentile"]
                total_agix_reward = data["total_agix_reward"]
                min_voting_weight = data["min_voting_weight"]
                max_voting_weight = data["max_voting_weight"]
            except Exception as e:
                error_message = (
                    f"The submitted data contained an invalid item: {repr_exception(e)}"
                )
                raise e

            # Calculate reward distribution
            try:
                wf.calculate_rewards(
                    filtered_user_ids,
                    function_agix_reward,
                    function_voting_weight,
                    threshold_percentile,
                    total_agix_reward,
                    min_voting_weight,
                    max_voting_weight,
                )
            except Exception as e:
                error_message = f"Reward calculation failed: {repr_exception(e)}"
                raise e

            # Convert SQLite to Excel file
            try:
                wf.convert_sqlite_to_excel()
            except Exception as e:
                error_message = (
                    "Convertion of SQLite file to Excel file "
                    f"failed: {repr_exception(e)}"
                )
                raise e

            # Create visualizations
            try:
                wf.create_visualizations()
            except Exception as e:
                error_message = (
                    f"Creation of visualizations failed: {repr_exception(e)}"
                )
                raise e

            # Create report
            try:
                wf.create_report()
            except Exception as e:
                error_message = f"Creation of report failed: {repr_exception(e)}"
                raise e

            # Create zip file with all results
            try:
                wf.create_zip_file()
            except Exception as e:
                error_message = (
                    f"Creation of zip file with results failed: {repr_exception(e)}"
                )
                raise e

            # Prepare data for successful step
            context = {
                "step": 5,
                "state": wf.state,
            }
        except Exception:
            # Prepare data for failed step
            context = {
                "step": 4,
                "calculate_rewards_form": calculate_rewards_form,
                "calculate_rewards_error_message": error_message,
                "state": wf.state,
            }

        response = render(request, self.template_name, context)
        return response

    def handle_default(self, request):
        raise Http404("Requested resource not found.")


class FileDownloader(View):
    def get(self, request, filename, *args, **kwargs):
        wf = aw.Workflow(request)
        session_key = wf.state.session.session_key
        dirpath = wf.state.dirpath
        filepath = os.path.join(dirpath, filename)
        if session_key is not None and os.path.isfile(filepath):
            # https://code.djangoproject.com/ticket/29278 => Do not use a context manager here!
            response = FileResponse(open(filepath, "rb"))
            response["Content-Type"] = "application/octet-stream"
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
        else:
            response = HttpResponseNotFound("File not found.")
        return response


# Forms


class ZipFileUploadForm(forms.Form):
    select_button = forms.FileField(
        label="",
        widget=forms.FileInput(attrs={"id": "zip-file-select-button"}),
        validators=[FileExtensionValidator(allowed_extensions=["zip"])],
    )
    upload_button = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "type": "submit",
                "class": "btn",
                "id": "zip-file-upload-button",
                "value": "Upload",
            }
        ),
        required=False,
    )


class FilterForm(forms.Form):
    def __init__(self, *args, missions=None, **kwargs):
        super().__init__(*args, **kwargs)

        if missions is None:
            missions = []
        for row in missions:
            m_id = str(row[0])
            m_title = str(row[1])
            self.fields[m_id] = forms.BooleanField(
                initial=False, required=False, label=m_title
            )

        self.fields["filter_button"] = forms.CharField(
            widget=forms.TextInput(
                attrs={
                    "type": "submit",
                    "name": "filter-button",
                    "class": "btn",
                    "value": "Apply",
                }
            ),
            label="",
            required=False,
        )

    def clean(self):
        cleaned_data = super().clean()

        for field_name in self.fields.keys():
            if field_name in self.data:
                field_value = self.data.get(field_name)
                field_value = True if field_value in ("on", True) else False
                cleaned_data[field_name] = field_value
        return cleaned_data


class CalculateScoresForm(forms.Form):
    proposals_created = forms.FloatField(initial=0.0, label="Created proposals")
    ratings_created = forms.FloatField(initial=0.0)
    ratings_received = forms.FloatField(initial=0.0)
    comments_created = forms.FloatField(initial=3.0)
    comments_received = forms.FloatField(initial=0.0)
    upvote_reactions_created = forms.FloatField(initial=0.0)
    downvote_reactions_created = forms.FloatField(initial=0.0)
    celebrate_reactions_created = forms.FloatField(initial=0.0)
    clap_reactions_created = forms.FloatField(initial=0.0)
    curious_reactions_created = forms.FloatField(initial=0.0)
    genius_reactions_created = forms.FloatField(initial=0.0)
    happy_reactions_created = forms.FloatField(initial=0.0)
    hot_reactions_created = forms.FloatField(initial=0.0)
    laugh_reactions_created = forms.FloatField(initial=0.0)
    love_reactions_created = forms.FloatField(initial=0.0)
    anger_reactions_created = forms.FloatField(initial=0.0)
    sad_reactions_created = forms.FloatField(initial=0.0)
    upvote_reactions_received = forms.FloatField(initial=2.0)
    downvote_reactions_received = forms.FloatField(initial=-3.0)
    celebrate_reactions_received = forms.FloatField(initial=2.0)
    clap_reactions_received = forms.FloatField(initial=2.0)
    curious_reactions_received = forms.FloatField(initial=2.0)
    genius_reactions_received = forms.FloatField(initial=2.0)
    happy_reactions_received = forms.FloatField(initial=2.0)
    hot_reactions_received = forms.FloatField(initial=2.0)
    laugh_reactions_received = forms.FloatField(initial=2.0)
    love_reactions_received = forms.FloatField(initial=2.0)
    anger_reactions_received = forms.FloatField(initial=-2.0)
    sad_reactions_received = forms.FloatField(initial=-2.0)

    fraction_of_engagement_scores_for_highly_rated_proposals = forms.FloatField(
        initial=0.0
    )

    calculate_scores_button = forms.CharField(
        widget=forms.TextInput(
            attrs={"type": "submit", "class": "btn", "value": "Calculate"}
        ),
        label="",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.field_groups = [
            {
                "text": "Weights given to different user activities",
                "fields": [
                    "proposals_created",
                    "ratings_created",
                    "ratings_received",
                    "comments_created",
                    "comments_received",
                    "upvote_reactions_created",
                    "downvote_reactions_created",
                    "celebrate_reactions_created",
                    "clap_reactions_created",
                    "curious_reactions_created",
                    "genius_reactions_created",
                    "happy_reactions_created",
                    "hot_reactions_created",
                    "laugh_reactions_created",
                    "love_reactions_created",
                    "anger_reactions_created",
                    "sad_reactions_created",
                    "upvote_reactions_received",
                    "downvote_reactions_received",
                    "celebrate_reactions_received",
                    "clap_reactions_received",
                    "curious_reactions_received",
                    "genius_reactions_received",
                    "happy_reactions_received",
                    "hot_reactions_received",
                    "laugh_reactions_received",
                    "love_reactions_received",
                    "anger_reactions_received",
                    "sad_reactions_received",
                ],
            },
            {
                "text": (
                    "Influence of proposal ratings: "
                    "What fraction of the total score shall come from ratings?"
                ),
                "fields": [
                    "fraction_of_engagement_scores_for_highly_rated_proposals",
                ],
            },
        ]


class CalculateRewardsForm(forms.Form):
    function_agix_reward = forms.CharField(label="AGIX formula", initial="x**2")
    function_voting_weight = forms.CharField(
        label="Voting power formula", initial="x**2"
    )
    threshold_percentile = forms.FloatField(label="Threshold percentile", initial=10.0)
    total_agix_reward = forms.FloatField(label="Total AGIX reward", initial=100_000.0)
    min_voting_weight = forms.FloatField(label="Minimum voting weight", initial=1.0)
    max_voting_weight = forms.FloatField(label="Maximum voting weight", initial=5.0)

    calculate_rewards_button = forms.CharField(
        widget=forms.TextInput(
            attrs={"type": "submit", "class": "btn", "value": "Calculate"}
        ),
        label="",
        required=False,
    )

    def __init__(self, *args, users=None, **kwargs):
        super().__init__(*args, **kwargs)

        if users is None:
            users = []
        user_ids = [str(row[0]) for row in users]
        for row in users:
            user_id = str(row[0])
            self.fields[user_id] = forms.BooleanField(
                initial=False, required=False, label=user_id
            )

        self.field_groups = [
            {
                "text": "Functions used for reward distribution",
                "fields": [
                    "function_agix_reward",
                    "function_voting_weight",
                    "threshold_percentile",
                    "total_agix_reward",
                    "min_voting_weight",
                    "max_voting_weight",
                ],
            },
            {
                "text": "Users to exclude from the reward distribution",
                "fields": user_ids,
            },
        ]


def repr_exception(e):
    return f"{type(e).__name__} - {str(e)}"
