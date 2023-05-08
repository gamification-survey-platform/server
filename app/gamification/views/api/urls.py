from django.urls import path
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import permissions

from app.gamification.views.api.artifact_review import ArtifactReviewDetails, AssignmentArtifactReviewList, UserArtifactReviewList, ArtifactReviewIpsatization
from app.gamification.views.api.artifacts import AssignmentArtifact, ArtifactDetail
from .user import UserDetail, Login, Register
from .course import CourseList, CourseDetail
from .assignment import AssignmentList, AssignmentDetail
from .survey import SurveyGetInfo
from .answer import ArtifactAnswerMultipleChoiceList, ArtifactAnswerKeywordList
from .reward import RewardList, RewardDetail, CourseRewardList, CourseRewardPurchases, CourseRewardPurchasesDetail, UserRewardPurchases, CourseRewardDetail
from .feedback_survey import SurveyList
from .member import MemberList
from .report import ViewReport

from drf_yasg.views import get_schema_view
from drf_yasg.utils import swagger_auto_schema
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

class APIRootView(generics.RetrieveAPIView):
     swagger_schema = None
     permission_classes = [permissions.AllowAny]
     @swagger_auto_schema(
          operation_description='Welcome message to API',
          tags=['root'],
          responses={
               200: openapi.Response(description='Successfully reached API')
          }
     )
     def get(self, request):
          return Response({ 'message': 'Welcome to the Gamification Platform API' }, status=200)

urlpatterns = [
     path('', APIRootView.as_view(), name='api-root'),
     path('swagger/', schema_view.with_ui('swagger',
          cache_timeout=0), name='schema-swagger-ui'),
     path('redoc/', schema_view.with_ui('redoc',
          cache_timeout=0), name='schema-redoc'),

     # GET or PATCH user by id
     path('users/<str:user_id>/', UserDetail.as_view(), name='user-detail'),

     # Login and Registration
     path('login/', Login.as_view(), name='user-login'),
     path('register/', Register.as_view(), name='user-register'),

     # GET user courses
     # POST course
     path('courses/', CourseList.as_view(), name='course-list'),

     # GET, PATCH, DELETE course by id
     path('courses/<str:course_id>/', CourseDetail.as_view(), name='course-detail'),

     # GET, POST course assignments
     path('courses/<str:course_id>/assignments/',
         AssignmentList.as_view(), name='assignment-list'),

    # GET, PATCH, DELETE, course assignment by id
    path('courses/<str:course_id>/assignments/<str:assignment_id>/',
         AssignmentDetail.as_view(), name='assignment-detail'),

     # GET, POST, DELETE member from course
     path('courses/<str:course_id>/members/',
          MemberList.as_view(), name='member-list'),


    # POST, GET artifact for an assignment
    path('courses/<str:course_id>/assignments/<str:assignment_id>/artifacts/',
         AssignmentArtifact.as_view(), name="submit-artifact"),

    # GET artifact by id
    path('courses/<str:course_id>/assignments/<str:assignment_id>/artifacts/<str:artifact_id>/',
         ArtifactDetail.as_view(), name="submit-artifact"),
]
'''


    # Report
    path('courses/<str:course_id>/assignments/<str:assignment_id>/reports/',
         ViewReport.as_view(), name='artifact-review-list'),

    # Get the  feedback_surveys, Post a new survey,update a survey
    path('courses/<str:course_id>/assignments/<str:assignment_id>/feedback_surveys/',
         SurveyList.as_view(), name='survey-list'),

    # get all sections, questions, options of a survey
    path('courses/<str:course_id>/assignments/<str:assignment_id>/surveys/',
         SurveyGetInfo.as_view(), name='survey-get-info'),



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

    # get course purchases
    path('courses/<str:course_id>/purchases/',
         CourseRewardPurchases.as_view(), name='reward-list'),

    # patch course purchases
    path('courses/<str:course_id>/purchases/<str:purchase_id>/',
         CourseRewardPurchasesDetail.as_view(), name='reward-list'),

    # get user purchases
    path('purchases/',
         UserRewardPurchases.as_view(), name='reward-list'),

    # get reward detail by reward_id, update a reward, delete a reward
    path('courses/<str:course_id>/rewards/<str:reward_id>/',
         CourseRewardDetail.as_view(), name='reward-detail'),
]
'''