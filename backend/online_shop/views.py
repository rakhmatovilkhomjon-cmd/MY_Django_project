from django.shortcuts import redirect, render
from .forms import (
    
    
    PostsForm,
    
)
from .models import  Posts



def home(request):
    text = "Hello world"
    return render(request, "home.html", {"text": text})


def about(request):
    return render(request, "about.html")   

def posts(request):
    posts = Posts.objects.all()
    context = {
        "posts": posts
    }
    return render(request, "posts.html", context)

def create_post(request):
    context = {
         "form": PostsForm() 
    }
    if request.method == "POST":
        form = PostsForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect("posts")

    return render(request, "create_post.html", context)



def update_post(request, pk: int):
    post = Posts.objects.get(id=pk)

    context = {
         "form": PostsForm(instance=post) 
    }
    if request.method == "POST":
        form = PostsForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
        return redirect("posts")

    return render(request, "update_post.html", context) 


def delete_post(request, pk: int):
    post = Posts.objects.get(id=pk)
    if request.method == "POST":
        post.delete()
    return redirect("posts")


