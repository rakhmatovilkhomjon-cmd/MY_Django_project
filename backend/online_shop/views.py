from django.shortcuts import render

# Create your views here.


def home(request):
    text = "Hello world"
    return render(request, "home.html", {"text": text})


def about(request):
    return render(request, "about.html")    