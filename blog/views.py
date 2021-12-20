from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token
from django.template.loader import render_to_string
from .models import Blog
from datetime import date, timedelta
from django.utils import timezone
from .forms import PostForm, SignUpForm
from django.contrib.auth import login, logout, authenticate
from django.core.mail import send_mail
from django.contrib.auth.models import User
#from django.contrib.auth.forms import UserCreationForm

currentdate = date.today()
currentdate += timedelta(days=1)
blogs_definition = ''

def all_blogs(request):
    blogs_definition = 'All Entries'
    loggeduser = None
    if request.user.is_authenticated:
        loggeduser = request.user.first_name + ' ' + request.user.last_name
    blogs = Blog.objects.order_by('-date').filter(date__range=["2001-01-01", currentdate]).select_related('author')
    return render(request, 'blog/all_blogs.html', {'blogs':blogs, 'definition':blogs_definition, 'loggeduser':loggeduser})

def recent_blogs(request):
    blogs_definition = 'Recent Entries'
    loggeduser = None
    if request.user.is_authenticated:
        loggeduser = request.user.first_name + ' ' + request.user.last_name
    blogs = Blog.objects.order_by('-date').filter(date__range=["2001-01-01", currentdate])[:5].select_related('author')
    return render(request, 'blog/all_blogs.html', {'blogs':blogs, 'definition':blogs_definition, 'loggeduser':loggeduser})

def logout_view(request):
    logout(request)

def new_entry(request):
    blogs_definition = 'Add New Entry'
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('all_blogs')
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form, 'definition':blogs_definition})

def signup_view(request):
    form = SignUpForm(request.POST)
    if form.is_valid():
        user = form.save()
        user.refresh_from_db()
        user.first_name = form.cleaned_data.get('first_name')
        user.last_name = form.cleaned_data.get('last_name')
        user.email = form.cleaned_data.get('email')
        #This part is because user ain't supposed to login until he confirmed registration through link
        user.is_active = False
        user.save()
        current_site = get_current_site(request)
        subject = 'Please Activate Your Account'
            # load a template like get_template()
            # and calls its render() method immediately.
        message = render_to_string('blog/activation_request.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            # method will generate a hash value with user related data
            'token': account_activation_token.make_token(user),
        })
        user.email_user(subject, message)
        #return redirect('activation_sent')
        return render(request, 'blog/activation_sent.html', {'message': message})
    else:
        form = SignUpForm()
    return render(request, 'blog/signup.html', {'form': form})

        #username = form.cleaned_data.get('username')
        #password = form.cleaned_data.get('password1')
        #user = authenticate(username=username, password=password)
        #login(request, user)
        #return redirect('all_blogs')
    #else:
    #    form = SignUpForm()
    #return render(request, 'blog/signup.html', {'form': form})

def activation_sent_view(request):
    return render(request, 'blog/activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true
        user.is_active = True
        # set signup_confirmation true
        user.profile.signup_confirmation = True
        user.save()
        login(request, user)
        return redirect('all_blogs')
    else:
        return render(request, 'blog/activation_invalid.html')
