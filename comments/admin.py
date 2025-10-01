from django.contrib import admin
from .models import Comment

# Register your models here.

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "content", "created_at")
    search_fields = ("content", "user__username", "article__title")
    list_filter = ("created_at",)
