from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str
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
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import CommentForm
from django.utils.text import slugify

currentdate = date.today()
currentdate += timedelta(days=1)
blogs_definition = ''

class BlogList(ListView):
    queryset = Blog.objects.filter(status=1).order_by('-date').select_related('author')
    template_name = 'blog/all_blogs.html'
    paginate_by = 5
    
class BlogDetail(DetailView):
    model = Blog
    template_name = 'blog/blog_detail.html'

def blog_detail(request, slug):
    template_name = 'blog/blog_detail.html'
    blog = get_object_or_404(Blog, slug=slug)
    comments = blog.comments.filter(active=True)
    new_comment = None
    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.blog = blog
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, template_name, {'blog': blog,
                                           'comments': comments,
                                           'new_comment': new_comment,
                                           'comment_form': comment_form})

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
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form, 'definition':blogs_definition})

def user_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = '''Activate your Bard's Lair Account'''
            message = render_to_string('blog/activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            #return redirect('activation_sent_view')
            return render(request, 'blog/activation_sent.html')
    else:
        form = SignUpForm()
    return render(request, 'blog/signup.html', {'form': form})

def activation_sent_view(request):
    return render(request, 'blog/activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
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
        return redirect('home')
    else:
        return render(request, 'blog/activation_invalid.html')
