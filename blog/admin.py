from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Blog, Comment

class BlogAdmin(MarkdownxModelAdmin):
    list_display = ('title', 'slug', 'status', 'date')
    list_filter = ("status",)
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}

class CommentAdmin(MarkdownxModelAdmin):
    list_display = ('name', 'body', 'blog', 'date', 'active')
    list_filter = ('active', 'date')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment, CommentAdmin)
