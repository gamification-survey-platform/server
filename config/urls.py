"""gamification URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

import app.gamification.views.pages as page_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', page_views.dashboard, name='home'),
    path('signin/', page_views.signin, name='signin'),
    path('signup/', page_views.signup, name='signup'),
    path('signout/', page_views.signout, name='signout'),

    path('email_user/<str:andrew_id>/', page_views.email_user, name='email_user'),

    path('dashboard/', page_views.dashboard, name='dashboard'),
    path('todo_list/', include([
        path('add/', page_views.add_todo_list, name='add_todo_list'),
        #    path('<int:todo_list_id>/', page_views.todo_list_detail, name='todo_list_detail'),
        #    path('<int:todo_list_id>/edit/', page_views.edit_todo_list, name='edit_todo_list'),
        path('<int:todo_list_id>/delete/',
             page_views.delete_todo_list, name='delete_todo_list'),
    ])),

    path('profile/', page_views.profile, name='profile'),
    path('profile_edit/', page_views.profile_edit, name='profile_edit'),
    
    path('instructor_admin/', page_views.instructor_admin, name='instructor_admin'),

    path('test/', page_views.test, name='test'),
#     path('test2/', page_views.test2, name='test2'),
#     path('test3/', page_views.test3, name='test3'),
    path('test_survey_template/', page_views.test_survey_template,
         name='test_survey_template'),
    path('test_report/', page_views.test_report, name='test_report'),

    path('dashboard_card/', page_views.dashboard_card, name='dashboard_card'),
    path('data_visualization/', page_views.data_visualization, name='data_visualization'),
    path('course/', include([
        path('', page_views.course_list, name='course'),

        path('<int:course_id>/', include([
            path('delete/', page_views.delete_course, name='delete_course'),
            path('edit/', page_views.edit_course, name='edit_course'),
            path('view/', page_views.view_course, name='view_course'),

            path('assignment/', include([
                path('', page_views.assignment, name='assignment'),
                path('<int:assignment_id>/', include([
                    path('review_survey/', include([
                         path('', page_views.review_survey,
                              name='review_survey'),
                         path('<int:artifact_review_id>/fill_survey/', page_views.fill_survey,
                              name='fill_survey'),
                         ])),

                    path('delete/', page_views.delete_assignment,
                         name='delete_assignment'),
                    path('edit/', page_views.edit_assignment,
                         name='edit_assignment'),
                    path('view/', page_views.view_assignment,
                         name='view_assignment'),
                    path('report/', include([
                         path('', page_views.view_reports,
                         name='view_reports'),
                         path('<int:team_id>/team_list', page_views.team_list,
                         name='team_list'),
                    ])),

                    path('template/', include([
                         path('add/', page_views.add_survey, name='add_survey'),
                         path('edit/', include([
                              path('', page_views.edit_survey,
                                   name='edit_survey'),
                              path('preview/', page_views.edit_preview_survey,
                                   name='preview_survey'),
                              ])),
                         path('edit_survey_template/', page_views.edit_survey_template,
                              name='edit_survey_template'),
                         ])),

                    path('artifact/', include([
                        path('', page_views.artifact, name='artifact'),
                        path('admin/', page_views.artifact_admin,
                             name='artifact_admin'),
                        path('<int:artifact_id>/', include([
                            path('delete/', page_views.delete_artifact,
                                 name='delete_artifact'),
                            path('edit/', page_views.edit_artifact,
                                 name='edit_artifact'),
                            path('view/', page_views.view_artifact,
                                 name='view_artifact'),
                            path('download/', page_views.download_artifact,
                                 name='download_artifact'),
                        ])),
                    ])),
                ]))
            ])),


            path('member_list/', include([
                path('', page_views.member_list, name='member_list'),
                path('<str:andrew_id>/', include([
                    path('delete/', page_views.delete_member,
                         name='delete_member'),
                ])),
               path('<int:assignment_id>/', include([
                    path('<str:andrew_id>/', include([
                         path('report/', page_views.report,
                              name='report'),
                    ]))
               ]))
            ])),
        ])),
    ])),

    path('api/', include('app.gamification.views.api.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('reset_password/', page_views.PasswordResetView.as_view(),
         name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
