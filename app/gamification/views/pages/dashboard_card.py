from django.shortcuts import render

def dashboard_card(request):
    user = request.user
    return render(request, 'dashboard_card.html')