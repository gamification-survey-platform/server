from pytz import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from app.gamification.decorators import user_role_check
from app.gamification.forms import CourseForm
from app.gamification.models import Course, Registration


LA = timezone('America/Los_Angeles')


@login_required
def course_list(request):
    def get_registrations(user):
        registration = []
        for reg in Registration.objects.filter(users=user):
            if reg.userRole == Registration.UserRole.Student and reg.courses.visible == False:
                continue
            else:
                registration.append(reg)
        return registration

    if request.method == 'GET':
        form = CourseForm(label_suffix='')
        registration = get_registrations(request.user)
        context = {'registration': registration, 'form': form}
        return render(request, 'course.html', context)
    if request.method == 'POST':
        if request.user.is_staff:
            form = CourseForm(request.POST, label_suffix='')
            if form.is_valid():
                course = form.save()
                registration = Registration(
                    users=request.user, courses=course, userRole=Registration.UserRole.Instructor)
                registration.save()
        else:
            form = CourseForm(label_suffix='')

        return redirect('edit_course', course.id)


@login_required
@user_role_check(user_roles=Registration.UserRole.Instructor)
def delete_course(request, course_id):
    if request.method == 'GET':
        course = get_object_or_404(Course, pk=course_id)
        course.delete()
        return redirect('course')
    else:
        return redirect('course')


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA])
def edit_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES,
                          instance=course, label_suffix='')

        if form.is_valid():
            course = form.save()
        return redirect('course')

    else:
        form = CourseForm(instance=course)
        return render(request, 'edit_course.html', {'course': course, 'form': form})


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA, Registration.UserRole.Student])
def view_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'GET':

        registration = get_object_or_404(
            Registration, users=request.user, courses=course)

        if course.visible == False and registration.userRole == Registration.UserRole.Student:
            return redirect('course')

        context = {'course': course}
        return render(request, 'view_course_detail.html', context)
    else:
        return redirect('course')
