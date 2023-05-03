from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from app.gamification.views.api.artifact_review import ArtifactReviewDetails, AssignmentArtifactReviewList, UserArtifactReviewList, ArtifactReviewIpsatization
from app.gamification.views.api.artifacts import SubmitArtifact, GetArtifact
from .user import Users, UserDetail, Login, Register
from .course import CourseList, CourseDetail
from .assignment import AssignmentList, AssignmentDetail
from .survey import SurveyGetInfo
from .answer import ArtifactAnswerMultipleChoiceList, ArtifactAnswerKeywordList
from .profile import UserProfile
from .reward import RewardList, RewardDetail, CourseRewardList, CourseRewardDetail
from .levels import LevelList
from .xp_points import UpdateExp
from .feedback_survey import SurveyList
from .member import MemberList
from .report import ViewReport
from .grade import GradeList
from .deduction import DeductionList, DeductionDetail

from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi


# Create a schema view for Swagger UI
schema_view = get_schema_view(
    openapi.Info(
        title="Gamification API",
        default_version='v1',
        description="API for Gamification",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


@api_view(['GET', 'POST'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'courses': reverse('course-list', request=request, format=format),
        'surveys': reverse('survey-list', request=request, format=format),
        'sections': reverse('section-list', request=request, format=format),
        'questions': reverse('question-list', request=request, format=format),
        'options': reverse('option-list', request=request, format=format),
        'answers': reverse('answer-list', request=request, format=format),
        'template_section': reverse('template-section-list', request=request, format=format),
        'artifact_reviews': reverse('artifact-review-list', request=request, format=format),
        'constraints': reverse('constraint-list', request=request, format=format),
    })


urlpatterns = [
    path('', api_root),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),

    # get all users
    path('users/', Users.as_view(), name='user-list'),

    # get user detail or update user.is_staff
    path('users/<str:andrew_id>/', UserDetail.as_view(), name='user-detail'),

    # login
    path('login/', Login.as_view(), name='user-login'),

    # register
    path('register/', Register.as_view(), name='user-register'),

    # get user profile, or update user profile
    path('profile/', UserProfile.as_view(), name='user-profile'),

    # update exp_points, exp, level
    path('exp/', UpdateExp.as_view(), name='xp-points-list'),

    # course
    path('courses/', CourseList.as_view(), name='course-list'),

    # course detail
    path('courses/<str:course_id>/', CourseDetail.as_view(), name='course-detail'),

    # assignment
    path('courses/<str:course_id>/assignments/',
         AssignmentList.as_view(), name='assignment-list'),

    # assignment detail
    path('courses/<str:course_id>/assignments/<str:assignment_id>/',
         AssignmentDetail.as_view(), name='assignment-detail'),

    # Entity/member
    path('courses/<str:course_id>/members/',
         MemberList.as_view(), name='member-list'),

    # Report
    path('courses/<str:course_id>/assignments/<str:assignment_id>/reports/',
         ViewReport.as_view(), name='artifact-review-list'),

    # Grade
    path('courses/<str:course_id>/assignments/<str:assignment_id>/grades/',
         GradeList.as_view(), name='grade-review-list'),

    # Get the  feedback_surveys, Post a new survey,update a survey
    path('courses/<str:course_id>/assignments/<str:assignment_id>/feedback_surveys/',
         SurveyList.as_view(), name='survey-list'),

    # get all sections, questions, options of a survey
    path('courses/<str:course_id>/assignments/<str:assignment_id>/surveys/',
         SurveyGetInfo.as_view(), name='survey-get-info'),

    # post or get an artifact
    path('courses/<str:course_id>/assignments/<str:assignment_id>/artifacts/',
         SubmitArtifact.as_view(), name="submit-artifact"),

    # get artifact by artifact_id
    path('courses/<str:course_id>/assignments/<str:assignment_id>/artifacts/<str:artifact_id>/',
         GetArtifact.as_view(), name="submit-artifact"),

    # Get answers keywords of artifact review
    path('courses/<str:course_id>/assignments/<str:assignment_id>/artifacts/<int:artifact_pk>/keywords',
         ArtifactAnswerKeywordList.as_view(), name='artifact-answer-keyword'),

    # Get answers statistics for statistics bar chart
    # courses/course_id/assignments/assignment_id/artifacts/artifact_id/report
    path('courses/<str:course_id>/assignments/<str:assignment_id>/artifacts/<int:artifact_pk>/statistics',
         ArtifactAnswerMultipleChoiceList.as_view(), name='artifact-answer-statistics'),

    # create a artifact review for a user given a artifact
    path('courses/<str:course_id>/assignments/<str:assignment_id>/artifacts_reviews/',
         UserArtifactReviewList.as_view(), name="artifact-review-list"),

    # get all artifact reviews for a user
    path('artifact_reviews/',
         UserArtifactReviewList.as_view(), name="artifact-review-list"),

    # get all artifact reviews for an assignment
    path('courses/<str:course_id>/assignments/<str:assignment_id>/artifact_reviews/',
         AssignmentArtifactReviewList.as_view(), name="artifact-review-list"),

    # calculate ipsatized values from artifact_reviews and saved to 'score' in Grade
    path('courses/<str:course_id>/assignments/<str:assignment_id>/artifact_reviews/ipsatization/',
         ArtifactReviewIpsatization.as_view(), name="artifact-review-list"),

    # get survey details with answers, patch answers for an artifact review survey
    path('courses/<str:course_id>/assignments/<str:assignment_id>/artifact_reviews/<str:artifact_review_pk>/',
         ArtifactReviewDetails.as_view(), name='survey-detail'),

    # superuser get all rewards
    path('rewards/', RewardList.as_view(), name='reward-list'),

    # superuser patch reward
    path('rewards/<str:reward_id>/', RewardDetail.as_view(), name='reward-detail'),

    # get course rewards
    path('courses/<str:course_id>/rewards/',
         CourseRewardList.as_view(), name='reward-list'),

    # get reward detail by reward_id, update a reward, delete a reward
    path('courses/<str:course_id>/rewards/<str:reward_id>/',
         CourseRewardDetail.as_view(), name='reward-detail'),

    # get level detail
    path('levels/<str:level>/', LevelList.as_view(), name='level-detail')
]
