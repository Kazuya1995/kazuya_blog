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
    search_fields = ('title', 'content', 'content_rich')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ('-published_at', '-created_at')
    filter_horizontal = ('tags',)
    
    fieldsets = (
        ('基本情報', {
            'fields': ('title', 'slug', 'category', 'tags', 'status', 'published_at')
        }),
        ('コンテンツ', {
            'fields': ('content_rich', 'content'),
            'description': 'リッチエディタまたはMarkdownのどちらかを使用してください。リッチエディタが優先されます。'
        }),
        ('メタ情報', {
            'fields': ('featured_image', 'excerpt'),
            'classes': ('collapse',)
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
