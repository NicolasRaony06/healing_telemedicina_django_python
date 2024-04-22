from django.shortcuts import render

def index_html(request):
    if request.method == 'GET':
        return render(request, 'index.html')