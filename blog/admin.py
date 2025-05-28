from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Category, Tag, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):
    list_display = ('title', 'slug', 'category', 'status', 'published_at', 'created_at', 'updated_at')
    list_filter = ('status', 'category', 'tags', 'created_at', 'updated_at', 'published_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('category', 'tags')
    date_hierarchy = 'published_at'
    ordering = ('-published_at', '-created_at')
    filter_horizontal = ('tags',)
