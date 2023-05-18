from datetime import datetime

import pytz

from app.gamification.models.artifact_review import ArtifactReview
from app.gamification.models.feedback_survey import FeedbackSurvey


def check_survey_status(assignment):
    try:
        feedback_survey = FeedbackSurvey.objects.get(assignment=assignment)
    except FeedbackSurvey.DoesNotExist:
        return "feedback_survey_not_exist"
    due_date = feedback_survey.date_due.astimezone(pytz.timezone("America/Los_Angeles"))
    now = datetime.now().astimezone(pytz.timezone("America/Los_Angeles"))
    if due_date < now:
        return ArtifactReview.ArtifactReviewType.LATE
    else:
        return ArtifactReview.ArtifactReviewType.COMPLETED