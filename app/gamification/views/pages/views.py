from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from app.gamification.decorators import admin_required


@login_required
@admin_required(redirect_field_name=None, login_url='dashboard')
def instructor_admin(request):
    return render(request, 'instructor_admin.html')
