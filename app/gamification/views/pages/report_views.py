from pytz import timezone
from django.shortcuts import get_object_or_404, redirect, render
from app.gamification.models import Assignment, Course, CustomUser, Registration, Team, Membership, Artifact, Individual

LA = timezone('America/Los_Angeles')


def report(request, course_id, assignment_id, andrew_id):
    # user = request.user
    user = get_object_or_404(CustomUser, andrew_id=andrew_id)
    course = get_object_or_404(Course, pk=course_id)
    registration = get_object_or_404(
        Registration, users=user, courses=course)
    userRole = registration.userRole
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    assignment_type = assignment.assignment_type
    if assignment_type == "Individual":
        try:
            entity = Individual.objects.get(
                registration=registration, course=course)
            team_name = str(andrew_id)
        except Individual.DoesNotExist:
            # Create an Individual entity for the user
            individual = Individual(course=course)
            individual.save()
            membership = Membership(student=registration, entity=individual)
            membership.save()
            entity = Individual.objects.get(
                registration=registration, course=course)
            team_name = str(andrew_id)
    elif assignment_type == "Team":
        try:
            entity = Team.objects.get(registration=registration, course=course)
            team_name = entity.name
        except Team.DoesNotExist:
            # TODO: Alert: you need to be a member of the team to upload the artifact
            return redirect('assignment', course_id)
    else:
        return redirect('assignment', course_id)
    # find artifact id with assignment id and entity id
    # artifact = get_object_or_404(Artifact, assignment=assignment, entity=entity)
    try:
        artifact = Artifact.objects.get(assignment=assignment, entity=entity)
        artifact_exists_flag = True
        artifact_id = artifact.pk
        artifact_path = artifact.file.url
        artifact_url = r"/api/artifacts/" + str(artifact_id) + "/"
        artifact_answers_url = r"/api/artifacts/" + str(artifact_id) + r"/answers/statistics"
    except Artifact.DoesNotExist:
        print("artifact does not exist")
        artifact_exists_flag = False
        artifact_id = None
        artifact_path = None
        artifact_url = None
        artifact_answers_url = None
    context = {'user': user,
               'course': course,
               'entity': entity,
               'userRole': userRole,
               'artifact_url': artifact_url,
               'artifact_path': artifact_path,
               'team_name': team_name,
               "artifact_exists_flag": artifact_exists_flag,
               "artifact_answers_url": artifact_answers_url
               }
    return render(request, 'test-report.html', context)