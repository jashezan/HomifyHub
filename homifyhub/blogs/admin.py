from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "is_published", "created_at")
    list_filter = ("is_published", "created_at", "author")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_published",)
    raw_id_fields = ("author",)
