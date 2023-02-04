from pytz import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from app.gamification.forms import ProfileForm
from app.gamification.models import CustomUser


LA = timezone('America/Los_Angeles')


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES,
                           instance=user, label_suffix='')

        if form.is_valid():
            user = form.save()
            form = ProfileForm(instance=user)
        else:
            user = CustomUser.objects.get(andrew_id=user.andrew_id)

    else:
        form = ProfileForm(instance=user)

    return render(request, 'profile.html', {'user': user, 'form': form})

@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES,
                           instance=user, label_suffix='')

        if form.is_valid():
            user = form.save()
            form = ProfileForm(instance=user)
        else:
            user = CustomUser.objects.get(andrew_id=user.andrew_id)

    else:
        form = ProfileForm(instance=user)

    return render(request, 'profile_edit.html', {'user': user, 'form': form})

