from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status


from app.gamification.models import CustomUser
from app.gamification.serializers import UserSerializer
from app.gamification.views.api.artifact_review import ArtifactReviewDetails, ArtifactReviewList
from app.gamification.views.api.artifacts import SubmitArtifact
from .user import Users, UserDetail, Login, Register
from .course import CourseList
from .assignment import AssignmentList, AssignmentDetail
from .survey import OptionDetail, OptionList, QuestionDetail, QuestionList, QuestionOptionList, QuestionOptionDetail, SectionDetail, SectionList, SectionQuestionList, SurveyGetInfo,  SurveySectionList, TemplateSectionList
from .answer import AnswerList, AnswerDetail, ArtifactAnswerList, ArtifactAnswerMultipleChoiceList,  CheckAllDone, CreateArtifactAnswer, FeedbackDetail, SurveyComplete, ArtifactAnswerKeywordList
from .constraint import ConstraintDetail, ConstraintList, ActionConstraintProgressDetail, GradeConstraintProgressDetail, ConstraintProgress
from .feedback_survey import SurveyList, SurveyDetail
from .rule import getAllRuleProgress, getRulesProgressByContraint, getAllRules
from .member import MemberList
from .report import ViewReport
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
        #    'rules': reverse('rule-list', request=request, format=format),
        'constraints': reverse('constraint-list', request=request, format=format),
    })


urlpatterns = [
    path('', api_root),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),

#     # User API
    path('users/', Users.as_view(), name='user-list'),
    path('users/<str:andrew_id>/', UserDetail.as_view(), name='user-detail'),
    path('login/', Login.as_view(), name='user-login'),
    path('register/', Register.as_view(), name='user-register'),

    # course
    path('courses/', CourseList.as_view(), name='course-list'),

    # assignment 
    path('courses/<str:course_id>/assignments/', AssignmentList.as_view(), name='assignment-list'),

    # assignment detail
    path('courses/<str:course_id>/assignments/<str:assignment_id>/', AssignmentDetail.as_view(), name='assignment-detail'),

    # Entity/member
    path('courses/<str:course_id>/members/', MemberList.as_view(), name='member-list'),
    # Report
    path('courses/<str:course_id>/assignments/<str:assignment_id>/reports/', ViewReport.as_view(), name='artifact-review-list'),

    # Get the  feedback_surveys, Post a new survey,update a survey
    path('courses/<str:course_id>/assignments/<str:assignment_id>/feedback_surveys/', SurveyList.as_view(), name='survey-list'),
    
    # get all sections, questions, options of a survey
    path('courses/<str:course_id>/assignments/<str:assignment_id>/surveys/', SurveyGetInfo.as_view(), name='survey-get-info'),

    # post or get an artifact
    path('courses/<str:course_id>/assignments/<str:assignment_id>/artifacts/',
          SubmitArtifact.as_view(), name="submit-artifact"),

    # get all artifact reviews
    path('courses/<str:course_id>/assignments/<str:assignment_id>/artifact_reviews/',
           ArtifactReviewList.as_view(), name="artifact-review-list"),

    # get survey details with answers, patch answers for an artifact review survey
    path('courses/<str:course_id>/assignments/<str:assignment_id>/artifact_reviews/<str:artifact_review_pk>/', 
         ArtifactReviewDetails.as_view(), name='survey-detail'),




#     # Get answers keywords of artifact review
#     path('artifacts/<int:artifact_pk>/answers/keywords',
#          ArtifactAnswerKeywordList.as_view(), name='artifact-answer-keyword'),

     # Get answers statistics for statistics bar chart
     # courses/course_id/assignments/assignment_id/artifacts/artifact_id/report
     path('artifacts/<int:artifact_pk>/answers/statistics',
          ArtifactAnswerMultipleChoiceList.as_view(), name='artifact-answer-statistics'),

#     # Get list of constraints
#     path('constraints/', ConstraintList.as_view(), name='constraint-list'),

#     # Get detail of a constraint, Update a constraint, Delete a constraint
#     path('constraints/<str:url>/',
#          ConstraintDetail.as_view(), name='constraint-detail'),

#     # Get progress of a constraint
#     path('constraints/<str:url>/progress/',
#          ConstraintProgress.as_view(), name='constraint-progress'),

#     # Get progress of an action constraint, update progress of an action constraint, delete progress of an action constraint
#     path('constraints/<str:url>/progress/action',
#          ActionConstraintProgressDetail.as_view(), name='constraint-progress-detail'),

#     # Get progress of a grade constraint, update progress of a grade constraint, delete progress of a grade constraint
#     path('constraints/<str:url>/progress/grade',
#          GradeConstraintProgressDetail.as_view(), name='constraint-progress-detail'),
#     # path('constraints/<int:constraint_pk>/progress', ConstraintProgress.as_view(), name='constraint-progress'),

#     # get all rules
#     path('rules/', getAllRules.as_view(), name='rule-list'),

#     # get the progress of all rules
#     path('rules/progress/', getAllRuleProgress.as_view(), name='rule-progress'),

#     # get the progress of all rules by constraint id
#     path('rules/progress/<int:constraint_pk>',
#          getRulesProgressByContraint.as_view(), name='rule-progress'),
]
