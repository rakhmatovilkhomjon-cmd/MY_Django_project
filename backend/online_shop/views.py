from django.shortcuts import render
from .forms import PostsForm

# Create your views here.


def home(request):
    text = "Hello world"
    return render(request, "home.html", {"text": text})


def about(request):
    return render(request, "about.html")   

def posts(request):
    return render(request, "posts.html")

def create_post(request):
    context = {
         "form": PostsForm() 
    }
    return render(request, "create_post.html", context) 