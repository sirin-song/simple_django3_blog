from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Blog

admin.site.register(Blog, MarkdownxModelAdmin)