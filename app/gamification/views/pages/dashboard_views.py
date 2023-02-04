from pytz import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from app.gamification.forms import TodoListForm
from app.gamification.models import Registration
from app.gamification.models.todo_list import TodoList

LA = timezone('America/Los_Angeles')


@login_required
def dashboard(request):
    def get_registrations(user):
        registration = []
        for reg in Registration.objects.filter(users=user):
            if reg.userRole == Registration.UserRole.Student and reg.courses.visible == False:
                continue
            else:
                registration.append(reg)
        return registration

    def get_todo_list(user):
        return TodoList.objects.filter(user=user)

    if request.method == 'GET':
        andrew_id = request.user.andrew_id
        form = TodoListForm(label_suffix='')
        unsorted_registration = get_registrations(request.user)
        # TODO: sort registration by semester in a better way
        registration = sorted(unsorted_registration,
                              key=lambda x: x.courses.semester, reverse=True)
        todo_list = get_todo_list(request.user)
        # sort todo list by due date, excluding NoneType
        sorted_todo_list = sorted(
            todo_list, key=lambda x: x.due_date if x.due_date else now(), reverse=False)
        # TODO: change timezone
        time_now = now()
        user = request.user
        context = {'registration': registration, 'request_user': user, 'form': form,
                   'andrew_id': andrew_id, 'todo_list': sorted_todo_list, 'time_now': time_now}
        return render(request, 'dashboard.html', context)


@login_required
def add_todo_list(request):
    if request.method == 'POST':
        form = TodoListForm(request.POST, label_suffix='')
        if form.is_valid():
            # todo_list = form.save(commit=False)
            # todo_list.user = request.user
            form.save()
        else:
            print("form is not valid")
        return redirect('dashboard')


@login_required
def delete_todo_list(request, todo_list_id):
    if request.method == 'GET':
        todo_list = get_object_or_404(TodoList, pk=todo_list_id)
        # check if the user is the owner of the todo list
        user = request.user
        # if todo_list.user == user:
        #     todo_list.delete()
        #     return redirect('dashboard')
        todo_list.delete()
        return redirect('dashboard')
    else:
        print("not deleted")
        return redirect('dashboard')
