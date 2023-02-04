import os
from pytz import timezone
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import FileResponse
from app.gamification.decorators import user_role_check
from app.gamification.forms import ArtifactForm
from app.gamification.models import Assignment, Course, Registration, Team, Membership, Artifact, Individual
from app.gamification.models.artifact_review import ArtifactReview

LA = timezone('America/Los_Angeles')


def check_artifact_permisssion(artifact_id, user):
    artifact = get_object_or_404(Artifact, pk=artifact_id)
    entity = artifact.entity
    members = entity.members
    if user in members:
        return True
    else:
        return False

# TODO: remove redundant code in artifact section to improve performance in the future
# TODO: create a directory for each course_assignment_team to store the files


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA, Registration.UserRole.Student])
def artifact(request, course_id, assignment_id):
    course = get_object_or_404(Course, pk=course_id)
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    # TODO: rethink about permission control for staff(superuser) and instructor
    registration = get_object_or_404(
        Registration, users=request.user, courses=course)
    userRole = registration.userRole
    # TODO: check the assigment type.
    assignment_type = assignment.assignment_type
    if assignment_type == "Individual":
        try:
            entity = Individual.objects.get(
                registration=registration, course=course)
        except Individual.DoesNotExist:
            # Create an Individual entity for the user
            individual = Individual(course=course)
            individual.save()
            membership = Membership(student=registration, entity=individual)
            membership.save()
            entity = Individual.objects.get(
                registration=registration, course=course)
    elif assignment_type == "Team":
        try:
            entity = Team.objects.get(registration=registration, course=course)
        except Team.DoesNotExist:
            # TODO: Alert: you need to be a member of the team to upload the artifact
            print("you need to be a member of the team to upload the artifact")
            return redirect('assignment', course_id)
    else:
        return redirect('assignment', course_id)

    if request.method == 'POST':
        # if artifact exists, redirect to the artifact page
        if Artifact.objects.filter(assignment=assignment, entity=entity).exists():
            return redirect('artifact', course_id, assignment_id)

        form = ArtifactForm(request.POST, request.FILES, label_suffix='')
        if form.is_valid():
            artifact = form.save()
            if assignment_type == 'Team':
                team_members = [i.pk for i in entity.members]
                registrations = [i for i in Registration.objects.filter(
                    courses=course) if i.users.pk not in team_members]
                for registration in registrations:
                    if registration.userRole == Registration.UserRole.Student:
                        artifact_review = ArtifactReview(
                            artifact=artifact, user=registration)
                        artifact_review.save()
            else:
                registrations = [i for i in Registration.objects.filter(
                    courses=course) if i.id != registration.id]
                if registration.userRole == Registration.UserRole.Student:
                    for single_registration in registrations:
                        artifact_review = ArtifactReview(
                            artifact=artifact, user=single_registration)
                        artifact_review.save()
        else:
            print("form is not valid")
        artifacts = Artifact.objects.filter(
            assignment=assignment, entity=entity)
        context = {'artifacts': artifacts,
                   "course_id": course_id,
                   "assignment_id": assignment_id,
                   "course": course,
                   "userRole": userRole,
                   "assignment": assignment,
                   "entity": entity}
        return redirect('view_assignment', course_id, assignment_id)
        # return render(request, 'artifact.html', context)

    if request.method == 'GET':
        artifacts = Artifact.objects.filter(
            assignment=assignment, entity=entity)
        context = {'artifacts': artifacts,
                   "course_id": course_id,
                   "assignment_id": assignment_id,
                   "course": course,
                   "userRole": userRole,
                   "assignment": assignment,
                   "entity": entity}
        # return redirect('view_assignment', course_id, assignment_id)
        return render(request, 'artifact.html', context)

    else:
        return redirect('assignment', course_id)


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA])
def artifact_admin(request, course_id, assignment_id):
    course = get_object_or_404(Course, pk=course_id)
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    registration = get_object_or_404(
        Registration, users=request.user, courses=course)
    userRole = registration.userRole
    if request.method == 'GET':
        artifacts = Artifact.objects.filter(assignment=assignment)
        context = {'artifacts': artifacts,
                   "course_id": course_id,
                   "course": course,
                   "userRole": userRole,
                   "assignment": assignment}
        return render(request, 'artifact_admin.html', context)


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA, Registration.UserRole.Student])
def download_artifact(request, course_id, assignment_id, artifact_id):
    course = Course.objects.get(pk=course_id)
    registration = Registration.objects.get(
                users=request.user, courses=course)
    userRole = registration.userRole
    print('userRole: ', userRole)
    if check_artifact_permisssion(artifact_id, request.user) or userRole == Registration.UserRole.Instructor or userRole == Registration.UserRole.TA:
        artifact = get_object_or_404(Artifact, pk=artifact_id)
        if settings.USE_S3:
            from config.storages import MediaStorage
            storage = MediaStorage()
            filename = artifact.file.name
            filepath = storage.url(filename)
            response = FileResponse(storage.open(filename, 'rb'))
        else:
            filepath = artifact.file.path
            response = FileResponse(open(filepath, 'rb'))
        # TODO: return 404 if file does not exist
        return response
    else:
        return redirect('assignment', course_id)


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA, Registration.UserRole.Student])
def view_artifact(request, course_id, assignment_id, artifact_id):
    return redirect('view_assignment', course_id, assignment_id)
    if check_artifact_permisssion(artifact_id, request.user):
        artifact = get_object_or_404(Artifact, pk=artifact_id)
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        return render(request, 'view_artifact.html', {'course_id': course_id, 'assignment_id': assignment_id, 'assignment': assignment, 'artifact': artifact})
    else:
        return redirect('assignment', course_id)


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA, Registration.UserRole.Student])
def delete_artifact(request, course_id, assignment_id, artifact_id):
    if check_artifact_permisssion(artifact_id, request.user):
        print("check_artifact_permisssion delete_artifact True")
    else:
        return redirect('assignment', course_id)

    if request.method == 'GET':
        artifact = get_object_or_404(Artifact, pk=artifact_id)
        # delete the artifact file first
        artifact.file.delete()
        artifact.delete()
        return redirect('view_assignment', course_id, assignment_id)
        # return redirect('artifact', course_id, assignment_id)
    else:
        return redirect('artifact', course_id, assignment_id)


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA, Registration.UserRole.Student])
def edit_artifact(request, course_id, assignment_id, artifact_id):
    if check_artifact_permisssion(artifact_id, request.user):
        print("check_artifact_permisssion edit_artifact True")
    else:
        return redirect('assignment', course_id)

    artifact = get_object_or_404(Artifact, pk=artifact_id)
    old_file_path = artifact.file
    userRole = Registration.objects.get(
        users=request.user, courses=course_id).userRole
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if request.method == 'POST':
        form = ArtifactForm(request.POST, request.FILES,
                            instance=artifact, label_suffix='')
        if form.is_valid():
            # delete the artifact file first
            new_file = os.path.split(str(form.cleaned_data['file']))[1]
            if new_file == "False":
                # delete the artifact if "clear" is selected
                # print("old file deleted, old_file_path:", old_file_path)
                old_file_path.delete()
            artifact = form.save()
            return redirect('view_assignment', course_id, assignment_id)
        else:
            return render(request, 'edit_artifact.html', {'course_id': course_id, 'assignment_id': assignment_id, 'assignment': assignment, 'form': form, 'userRole': userRole})

    if request.method == 'GET':
        form = ArtifactForm(instance=artifact)
        return render(request, 'edit_artifact.html', {'course_id': course_id, 'assignment_id': assignment_id, 'assignment': assignment, 'form': form, 'userRole': userRole})

    else:
        return redirect('artifact', course_id, assignment_id)
