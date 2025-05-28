from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Post, Category, Tag

# Create your views here.

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(status='published').select_related('category').prefetch_related('tags')

    def get_categories(self):
        return Category.objects.all()

    def get_tags(self):
        return Tag.objects.all()


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(status='published').select_related('category').prefetch_related('tags')

    def get_categories(self):
        return Category.objects.all()

    def get_tags(self):
        return Tag.objects.all()


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category_post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            status='published',
            category=self.category
        ).select_related('category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

    def get_categories(self):
        return Category.objects.all()

    def get_tags(self):
        return Tag.objects.all()


class TagPostListView(ListView):
    model = Post
    template_name = 'blog/tag_post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(
            status='published',
            tags=self.tag
        ).select_related('category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context

    def get_categories(self):
        return Category.objects.all()

    def get_tags(self):
        return Tag.objects.all()
