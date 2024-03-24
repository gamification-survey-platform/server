from django.urls import path
from app.gamification.views.api.survey import SurveyDetail
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view
from rest_framework import generics, permissions
from rest_framework.response import Response

from app.gamification.views.api.artifact_review import (
    ArtifactReviewDetails,
    ArtifactReviewersList,
    ArtifactReviewIpsatization,
    ArtifactReviewStatus,
    AssignmentArtifactReviewList,
    UserArtifactReviewList,
    OptionalArtifactReview
)

from app.gamification.views.api.trivia import TriviaView
from app.gamification.views.api.triviaCompleted import MarkTriviaCompletedView
from app.gamification.views.api.artifacts import ArtifactDetail, AssignmentArtifact

from .answer import (
    ArtifactAnswerDetail,
    ArtifactAnswerKeywordList,
    ArtifactAnswerMultipleChoiceList,
)
from .assignment import AssignmentDetail, AssignmentList, AssignmentSurvey
from .course import CourseDetail, CourseList
from .leaderboard import CourseLeaderboard, PlatformLeaderboard
from .member import MemberList
from .team import TeamList
from .notification import NotificationDetail
from .reward import (
    CourseRewardDetail,
    CourseRewardList,
    CourseRewardPurchases,
    CourseRewardPurchasesDetail,
    RewardDetail,
    UserRewardPurchases,
)
from .theme import PublishedThemes, ThemeDetail
from .user import Login, Register, UserDetail, UserSurvey

# Create a schema view for Swagger UI
schema_view = get_schema_view(
    openapi.Info(
        title="Gamification API",
        default_version="v1",
        description="API for Gamification",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


class APIRootView(generics.RetrieveAPIView):
    swagger_schema = None
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Welcome message to API",
        tags=["root"],
        responses={200: openapi.Response(description="Successfully reached API")},
    )
    def get(self, request):
        return Response({"message": "Welcome to the Gamification Platform API."}, status=200)


urlpatterns = [
    path("", APIRootView.as_view(), name="api-root"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # GET or PATCH user by id
    path("users/<str:user_id>/", UserDetail.as_view(), name="user-detail"),
    # GET or PATCH user by theme
    path("themes/", ThemeDetail.as_view(), name="theme-detail"),
    # GET published themes
    path("published_themes/", PublishedThemes.as_view(), name="published-theme"),
    # POST Login and Registration
    path("login/", Login.as_view(), name="user-login"),
    path("register/", Register.as_view(), name="user-register"),
    # GET user courses
    # POST course
    path("courses/", CourseList.as_view(), name="course-list"),
    # GET trivia
    path(
        "courses/<str:course_id>/trivia", TriviaView.as_view(), name="course-trivia",
    ),
    # POST trivia completion by user
    path('trivia/<int:trivia_id>/complete', MarkTriviaCompletedView.as_view(), name='trivia-complete'),
    # GET, PATCH, DELETE course by id
    path("courses/<str:course_id>/", CourseDetail.as_view(), name="course-detail"),
    # GET, POST course assignments
    path("courses/<str:course_id>/assignments/", AssignmentList.as_view(), name="assignment-list"),
    # GET, PATCH, DELETE, course assignment by id
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/", AssignmentDetail.as_view(), name="assignment-detail"
    ),
    # GET, POST, DELETE member from course
    path("courses/<str:course_id>/members/", MemberList.as_view(), name="member-list"),
    # GET, POST, DELETE member from course
    path("courses/<str:course_id>/teams/", TeamList.as_view(), name="team-list"),
    # GET, POST, DELETE member from course
    # POST, GET artifact for an assignment
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/artifacts/",
        AssignmentArtifact.as_view(),
        name="submit-artifact",
    ),
    # GET artifact by id
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/artifacts/<str:artifact_id>/",
        ArtifactDetail.as_view(),
        name="submit-artifact",
    ),
    # Surveys are templates created by instructors --> used to create ArtifactReviews
    # GET, POST, PATCH survey based on assignment_id
    path(
        "assignments/<str:assignment_id>/surveys/",
        AssignmentSurvey.as_view(),
        name="survey-list",
    ),
    # GET all Surveys based on user_id
    path(
        "user/<str:user_id>/surveys/",
        UserSurvey.as_view(),
        name="user-survey",
    ),
    # GET, PATCH, DELETE survey template
    path(
        "surveys/<str:survey_pk>/",
        SurveyDetail.as_view(),
        name="survey-detail",
    ),
    # GET user artifact reviews
    path("artifact_reviews/", UserArtifactReviewList.as_view(), name="artifact-review-list"),
    # GET all artifact reviews for an assignment
    # POST, DELETE manually assign or unassign artifact review from student
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/artifact_reviews/",
        AssignmentArtifactReviewList.as_view(),
        name="artifact-review-list",
    ),
    # GET optional artifact reviews for an assignment
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/user/<str:user_id>/optional_review",
        OptionalArtifactReview.as_view(),
        name="optional-artifact-review",
    ),
    # GET all artifact reviewers for an assignment
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/artifacts/<str:artifact_id>/artifact_reviews/",
        ArtifactReviewersList.as_view(),
        name="artifact-review-list",
    ),
    # GET, PATCH artifact review
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/artifact_reviews/<str:artifact_review_pk>/",
        ArtifactReviewDetails.as_view(),
        name="survey-detail",
    ),
    # GET ipsatization results from artifact_reviews
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/artifact_reviews/ipsatization/",
        ArtifactReviewIpsatization.as_view(),
        name="artifact-review-list",
    ),
    # PATCH artifact review status
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/artifact_reviews/<str:artifact_review_pk>/status/",
        ArtifactReviewStatus.as_view(),
        name="artifact-review-status",
    ),
    # GET keywords from artifact reviews (for reports)
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/artifacts/<int:artifact_pk>/keywords",
        ArtifactAnswerKeywordList.as_view(),
        name="artifact-answer-keyword",
    ),
    # GET answers statistics for statistics bar chart
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/artifacts/<int:artifact_pk>/statistics",
        ArtifactAnswerMultipleChoiceList.as_view(),
        name="artifact-answer-statistics",
    ),
    # GET all answers for a artifact
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/artifacts/<int:artifact_pk>/answers",
        ArtifactAnswerDetail.as_view(),
        name="artifact-answer-detail",
    ),
    # Rewards
    # GET course rewards
    path("courses/<str:course_id>/rewards/", CourseRewardList.as_view(), name="reward-list"),
    # PATCH reward to purchase
    path("rewards/<str:reward_id>/", RewardDetail.as_view(), name="reward-detail"),
    # GET, PATCH, DELETE a reward by id
    path("courses/<str:course_id>/rewards/<str:reward_id>/", CourseRewardDetail.as_view(), name="reward-detail"),
    # GET course purchases
    path("courses/<str:course_id>/purchases/", CourseRewardPurchases.as_view(), name="reward-list"),
    # PATCH course purchases
    path(
        "courses/<str:course_id>/purchases/<str:purchase_id>/",
        CourseRewardPurchasesDetail.as_view(),
        name="reward-list",
    ),
    # POST notification
    path("notifications/", NotificationDetail.as_view(), name="notification-detail"),
    # GET user purchases
    path("purchases/", UserRewardPurchases.as_view(), name="reward-list"),
    # GET platform experience
    path("experience/", PlatformLeaderboard.as_view(), name="experience-list"),
    # GET course experience
    path("experience/<str:course_id>/", CourseLeaderboard.as_view(), name="experience-list"),
]
