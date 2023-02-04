from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .user import UserList, UserDetail
from .course import CourseList, CourseDetail
from .survey import OptionDetail, OptionList, QuestionDetail, QuestionList, QuestionOptionList, QuestionOptionDetail, SectionDetail, SectionList, SectionQuestionList, SurveyGetInfo, SurveyList, SurveyDetail, SurveySectionList, TemplateSectionList
from .answer import AnswerList, AnswerDetail, ArtifactAnswerList, ArtifactAnswerMultipleChoiceList, ArtifactReviewList, ArtifactReviewDetail, CheckAllDone, CreateArtifactReview, CreateArtifactAnswer, FeedbackDetail, ArtifactResult, SurveyComplete, ArtifactAnswerKeywordList
from .constraint import ConstraintDetail, ConstraintList, ActionConstraintProgressDetail, GradeConstraintProgressDetail, ConstraintProgress
from .rule import getAllRuleProgress, getRulesProgressByContraint, getAllRules

@api_view(['GET'])
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
    path('users/', UserList.as_view(), name='user-list'),
    path('users/<str:andrew_id>/', UserDetail.as_view(), name='user-detail'),
    path('courses/', CourseList.as_view(), name='course-list'),
    path('courses/<str:id>/', CourseDetail.as_view(), name='course-detail'),

    # RetrieveUpdateDestroyAPIView GET, PUT, PATCH, DELETE
    # ListAPIView GET
    # ListCreateAPIView GET POST


    # Get the list of all surveys, or Post a new survey
    path('surveys/', SurveyList.as_view(), name='survey-list'),

    # Get detail of a survey, Delete a survey, Update a survey
    path('surveys/<int:survey_pk>/', SurveyDetail.as_view(), name='survey-detail'),

    # get all sections, questions, options of a survey
    path('surveys/<int:survey_pk>/get_info/',
         SurveyGetInfo.as_view(), name='survey-get-info'),

    # Get the sections of a survey, Post a new section of the survey
    path('surveys/<int:survey_pk>/sections/',
         SurveySectionList.as_view(), name='survey-section-list'),

    # Get list of sections
    # ListAPIView
    path('sections/', SectionList.as_view(), name='section-list'),

    # List template sections
    path('template_sections/', TemplateSectionList.as_view(),
         name='template-section-list'),

    # Get detail of a section, Update a section, Delete a section
    path('sections/<int:section_pk>/',
         SectionDetail.as_view(), name='section-detail'),

    # Get list of questions of a section, Post a new question of the section
    path('sections/<int:section_pk>/questions/',
         SectionQuestionList.as_view(), name='section-question-list'),

    # Get list of questions
    path('questions/', QuestionList.as_view(), name='question-list'),

    # Get detail of a question, Update a question, Delete a question
    path('questions/<int:question_pk>/',
         QuestionDetail.as_view(), name='question-detail'),

    path('questions/<int:question_pk>/check_all_done/',
         CheckAllDone.as_view(), name="check-all-done"),

    # Get list of options of a question, Post a new option of the question
    path('questions/<int:question_pk>/options/',
         QuestionOptionList.as_view(), name='question-option-list'),

    # Update an option, Delete an option
    path('questions/<int:question_pk>/options/<int:option_pk>/',
         QuestionOptionDetail.as_view(), name='question-option-detail'),

    # Get list of options, Post a new option
    path('options/', OptionList.as_view(), name='option-list'),

    # Get detail of an option, Update an option, Delete an option
    path('options/<int:option_pk>/', OptionDetail.as_view(), name='option-detail'),

    # Get the list of all answers
    path('answers/', AnswerList.as_view(), name='answer-list'),

    # Get detail of answer, update an answer, delete an answer
    path('answers/<int:answer_pk>/', AnswerDetail.as_view(), name='answer-detail'),

    # Get answers of artifact review
    path('artifact_reviews/<int:artifact_review_pk>/answers/',
         ArtifactAnswerList.as_view(), name='artifact-answer'),

    # Get answers of a question, Post answer to artifact(response answer_pk)
    path('artifact_reviews/<int:artifact_review_pk>/questions/<question_pk>/answers/',
         CreateArtifactAnswer.as_view(), name='create-artifact-answer'),

    # Get list of artifact reviews
    path('artifact_reviews/', ArtifactReviewList.as_view(),
         name="artifact-review-list"),

    # Get detail of an artifact review. delete an artifact review
    path('artifact_reviews/<int:artifact_review_id>/',
         ArtifactReviewDetail.as_view(), name="artifact-review-detail"),

    path('artifact_reviews/<int:artifact_review_pk>/is_complete/',
         SurveyComplete.as_view(), name="survey-complete"),

    # Get artifact review of an artifact, post a new artifact review
    path('artifact_reviews/<int:artifact_pk>/<int:registration_pk>',
         CreateArtifactReview.as_view(), name="artifact-review"),

    path('artifacts/<int:artifact_pk>/',
         ArtifactResult.as_view(), name="artifact-result"),

      # Get answers keywords of artifact review
    path('artifacts/<int:artifact_pk>/answers/keywords',
         ArtifactAnswerKeywordList.as_view(), name='artifact-answer-keyword'),

     # Get answers statistics for statistics bar chart
     path('artifacts/<int:artifact_pk>/answers/statistics',
           ArtifactAnswerMultipleChoiceList.as_view(), name='artifact-answer-statistics'),

     # Get list of constraints
     path('constraints/', ConstraintList.as_view(), name='constraint-list'),

     # Get detail of a constraint, Update a constraint, Delete a constraint
     path('constraints/<str:url>/',
          ConstraintDetail.as_view(), name='constraint-detail'),

     # Get progress of a constraint
     path('constraints/<str:url>/progress/',
          ConstraintProgress.as_view(), name='constraint-progress'),

     # Get progress of an action constraint, update progress of an action constraint, delete progress of an action constraint
     path('constraints/<str:url>/progress/action',
          ActionConstraintProgressDetail.as_view(), name='constraint-progress-detail'),
     
     # Get progress of a grade constraint, update progress of a grade constraint, delete progress of a grade constraint
     path('constraints/<str:url>/progress/grade',
          GradeConstraintProgressDetail.as_view(), name='constraint-progress-detail'),
     # path('constraints/<int:constraint_pk>/progress', ConstraintProgress.as_view(), name='constraint-progress'),

     # get all rules
     path('rules/', getAllRules.as_view(), name='rule-list'),
     
     # get the progress of all rules
     path('rules/progress/', getAllRuleProgress.as_view(), name='rule-progress'),
     
     # get the progress of all rules by constraint id
     path('rules/progress/<int:constraint_pk>', getRulesProgressByContraint.as_view(), name='rule-progress'),
]
     
