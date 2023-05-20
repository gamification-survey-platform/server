from django.urls import path
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view
from rest_framework import generics, permissions
from rest_framework.response import Response

from app.gamification.views.api.artifact_review import (
    ArtifactReviewDetails,
    ArtifactReviewIpsatization,
    AssignmentArtifactReviewList,
    UserArtifactReviewList,
)
from app.gamification.views.api.artifacts import ArtifactDetail, AssignmentArtifact

from .answer import ArtifactAnswerKeywordList, ArtifactAnswerMultipleChoiceList
from .assignment import AssignmentDetail, AssignmentList
from .course import CourseDetail, CourseList
from .feedback_survey import SurveyDetail, SurveyList
from .member import MemberList
from .reward import (
    CourseRewardDetail,
    CourseRewardList,
    CourseRewardPurchases,
    CourseRewardPurchasesDetail,
    UserRewardPurchases,
)
from .survey import SurveyGetInfo
from .theme import ThemeDetail
from .user import Login, Register, UserDetail

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
        return Response({"message": "Welcome to the Gamification Platform API"}, status=200)


urlpatterns = [
    path("", APIRootView.as_view(), name="api-root"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # GET or PATCH user by id
    path("users/<str:user_id>/", UserDetail.as_view(), name="user-detail"),
    # GET or PATCH user by theme
    path("theme/", ThemeDetail.as_view(), name="theme-detail"),
    # POST Login and Registration
    path("login/", Login.as_view(), name="user-login"),
    path("register/", Register.as_view(), name="user-register"),
    # GET user courses
    # POST course
    path("courses/", CourseList.as_view(), name="course-list"),
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
    # GET, POST survey for an assignment
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/feedback_surveys/",
        SurveyList.as_view(),
        name="survey-list",
    ),
    # GET all Survey contents - details, sections, questions
    path(
        "courses/<str:course_id>/assignments/<str:assignment_id>/surveys/",
        SurveyGetInfo.as_view(),
        name="survey-get-info",
    ),
    # PATCH, DELETE survey template
    path(
        "feedback_surveys/<str:feedback_survey_pk>",
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
    # Rewards
    # GET course rewards
    path("courses/<str:course_id>/rewards/", CourseRewardList.as_view(), name="reward-list"),
    # superuser patch reward
    # path('rewards/<str:reward_id>/', RewardDetail.as_view(), name='reward-detail'),
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
    # GET user purchases
    path("purchases/", UserRewardPurchases.as_view(), name="reward-list"),
]
