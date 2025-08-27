from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import BlogPost


class BlogListView(ListView):
    """
    View for listing all blog posts.
    """

    model = BlogPost
    template_name = "blogs/blog_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).order_by("-created_at")


class BlogDetailView(DetailView):
    """
    View for displaying a single blog post.
    """

    model = BlogPost
    template_name = "blogs/blog_post.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)
