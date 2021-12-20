from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_blogs, name='all_blogs'),
    path('recent/', views.recent_blogs, name='recent_blogs'),
    path('new/', views.new_entry, name='new_entry'),
]