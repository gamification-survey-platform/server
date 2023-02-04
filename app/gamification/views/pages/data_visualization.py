from django.shortcuts import render

def data_visualization(request):
    # user = request.user
    return render(request, 'data_visualization.html')