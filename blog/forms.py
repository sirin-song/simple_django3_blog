from django import forms
from .models import Blog, Comment
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core import validators

class PostForm(forms.ModelForm):

    class Meta:
        model = Blog
        fields = ('title', 'description',)

class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30, help_text ='Required. Used for logging in. Max length 30 characters')
    first_name = forms.CharField(max_length=150) #, help_text='First Name')
    last_name = forms.CharField(max_length=150) #, help_text='Last Name')
    email = forms.EmailField(max_length=200, help_text='Required. Enter a valid email address')

    def clean_username(self):
        nom_de_guerre=self.cleaned_data['username']
        if User.objects.filter(username=nom_de_guerre).exists():
            raise forms.ValidationError('User with this name is already exists!')
        return nom_de_guerre

    def clean_email(self):
        addresse_de_mail=self.cleaned_data['email']
        if User.objects.filter(email=addresse_de_mail).exists():
            raise forms.ValidationError('User with this email is already exists!')
        return addresse_de_mail

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
