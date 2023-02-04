from pytz import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from app.gamification.decorators import admin_required
from app.gamification.forms import SignUpForm, PasswordResetForm
from app.gamification.models import CustomUser


LA = timezone('America/Los_Angeles')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, label_suffix='')
        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect('profile')
    else:
        form = SignUpForm(label_suffix='')

    return render(request, 'signup.html', {'form': form})


def signin(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to where they were asked to login
                return redirect('profile')
    else:
        form = AuthenticationForm()

    return render(request=request, template_name="signin.html", context={"form": form})


class PasswordResetView(auth_views.PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'password_reset.html'


def signout(request):
    logout(request)
    return redirect('signin')


@admin_required
def email_user(request, andrew_id):
    current_site = get_current_site(request)
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, andrew_id=andrew_id)

        subject = 'Gamification: Activate your account'
        message = 'Please click the link below to reset your password, '\
            'and then login into the system to activate your account:\n\n'
        message += f'http://{current_site.domain}{reverse("password_reset")}\n\n'
        message += 'Your Andrew ID: ' + user.andrew_id + '\n\n'
        message += 'If you did not request this, please ignore this email.\n'

        user.email_user(subject, message)

        redirect_path = request.POST.get('next', reverse('dashboard'))
        messages.info(request, f'An email has been sent to {user.andrew_id}.')
    elif request.method == 'GET':
        redirect_path = request.GET.get('next', reverse('dashboard'))
    else:
        redirect_path = reverse('dashboard')

    return redirect(redirect_path)
