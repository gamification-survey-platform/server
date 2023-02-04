import pytz
from pytz import timezone
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from app.gamification.decorators import user_role_check
from app.gamification.models import Assignment, Course, CustomUser, Registration, Team, Membership, Artifact
from app.gamification.models.artifact_review import ArtifactReview

LA = timezone('America/Los_Angeles')


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA, Registration.UserRole.Student])
def member_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    # TODO: rethink about permission control for staff(superuser) and instructor
    registration = get_object_or_404(
        Registration, users=request.user, courses=course)
    userRole = registration.userRole

    def get_member_list(course_id):
        registration = Registration.objects.filter(courses=course)
        membership = []
        for i in registration:
            try:
                get_registration_team = Team.objects.filter(registration=i)
                if len(get_registration_team) > 1:
                    team = get_registration_team[len(
                        get_registration_team) - 1].name
                else:
                    team = Team.objects.get(registration=i).name
            except Team.DoesNotExist:
                team = ''
            membership.append({
                'andrew_id': i.users.andrew_id,
                'userRole': i.userRole,
                'team': team,
                'is_activated': i.users.is_activated,
            })
        membership = sorted(membership, key=lambda x: x['team'])
        context = {'membership': membership,
                   'course_id': course_id, 'userRole': userRole}
        return context

    # Create registration for user who is not registered this course, otherwise, return the registration
    def get_users_registration(users, request):
        andrew_id = request.POST['andrew_id']
        role = request.POST['membershipRadios']
        if user not in users:
            registration = Registration(
                users=user, courses=course, userRole=role)
            registration.save()
            message_info = 'A new member has been added'
            assignments = []
            for a in Assignment.objects.filter(course=course, assignment_type=Assignment.AssigmentType.Individual):
                if a.date_due != None and a.date_due.astimezone(pytz.timezone('America/Los_Angeles')) < datetime.now().astimezone(pytz.timezone('America/Los_Angeles')):
                    assignments.append(a)
                elif a.date_due == None:
                    assignments.append(a)
            for assignment in assignments:
                artifacts = Artifact.objects.filter(assignment=assignment)
                for artifact in artifacts:
                    artifact_review = ArtifactReview(
                        artifact=artifact, user=registration)
                    artifact_review.save()
        else:
            registration = get_object_or_404(
                Registration, users=user, courses=course)
            registration.userRole = role
            registration.save()

            message_info = andrew_id + '\'s team has been added or updated'
        return registration, message_info

    # Create membership for user's team
    def get_users_team(registration, request):
        team_name = request.POST['team_name']
        if team_name != '' and registration.userRole == 'Student':
            team = registration.team
            if team is not None:
                membership = get_object_or_404(
                    Membership, student=registration, entity=team)
                membership.delete()
                if len(team.members) == 0:
                    team.delete()
                else:
                    # add artifact_review for previous team
                    artifacts = Artifact.objects.filter(entity=team)
                    for artifact in artifacts:
                        artifact_review = ArtifactReview(
                            artifact=artifact, user=registration)
                        artifact_review.save()

            try:
                team = Team.objects.get(
                    course=course, name=team_name)
            except Team.DoesNotExist:
                team = Team(course=course, name=team_name)
                team.save()
            membership = Membership(
                student=registration, entity=team)
            membership.save()
            # delete artifact review for updated team
            artifacts = Artifact.objects.filter(entity=team)
            for artifact in artifacts:
                ArtifactReview.objects.filter(
                    artifact=artifact, user=registration).delete()

    # Create a list of users in the course

    def add_users_from_the_same_course():
        users = []
        users.extend(course.students)
        users.extend(course.TAs)
        users.extend(course.instructors)
        return users

    # Delete ta and instructor membership if he/she is student before
    def delete_memebership_after_switch_to_TA_or_instructor(registration):
        if registration.userRole == 'TA' or registration.userRole == 'Instructor':
            membership = Membership.objects.filter(student=registration)
            if len(membership) == 1:
                team = Team.objects.filter(
                    registration=registration, course=course)
                if len(team) == 1:
                    team = team[0]
                members = team.members
                if len(members) == 1:
                    team.delete()
            membership.delete()
            # delete all artifact_review of TA or instructor
            artifact_reviews = ArtifactReview.objects.filter(user=registration)
            for artifact_review in artifact_reviews:
                artifact_review.delete()

    if request.method == 'GET':
        context = get_member_list(course_id)
        return render(request, 'course_member.html', context)
    elif request.method == 'POST' and userRole != 'Student':
        andrew_id = request.POST['andrew_id']
        try:
            user = CustomUser.objects.get(andrew_id=andrew_id)
            users = add_users_from_the_same_course()
            registration, message_info = get_users_registration(
                users, request)
            delete_memebership_after_switch_to_TA_or_instructor(
                registration)
            get_users_team(registration, request)
        except CustomUser.DoesNotExist:
            message_info = 'AndrewID does not exist'
        messages.info(request, message_info)
        context = get_member_list(course_id)
        return render(request, 'course_member.html', context)
    else:
        return redirect('member_list', course_id)


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA])
def delete_member(request, course_id, andrew_id):
    if request.method == 'GET':
        user = get_object_or_404(CustomUser, andrew_id=andrew_id)
        registration = get_object_or_404(
            Registration, users=user, courses=course_id)
        membership = Membership.objects.filter(student=registration)
        membership.delete()
        registration.delete()
        return redirect('member_list', course_id)
    else:
        return redirect('member_list', course_id)
