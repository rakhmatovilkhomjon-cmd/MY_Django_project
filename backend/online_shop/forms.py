from django import forms
from .models import  Posts 




class PostsForm(forms.ModelForm):
    # title = forms.CharField(max_length=255)
    # content = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Posts
        fields = "__all__"


