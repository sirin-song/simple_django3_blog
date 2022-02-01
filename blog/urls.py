from django.urls import path
from . import views

urlpatterns = [
    path('', views.BlogList.as_view(), name='home'),
    path('new/', views.new_entry, name='new_entry'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
]
