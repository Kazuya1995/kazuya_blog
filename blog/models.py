from django.db import models
from django.utils import timezone
from django.urls import reverse
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from ckeditor_uploader.fields import RichTextUploadingField


class Category(models.Model):
    name = models.CharField('カテゴリ名', max_length=255)
    slug = models.SlugField('URLスラッグ', unique=True)
    description = models.TextField('説明', blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'カテゴリ'
        verbose_name_plural = 'カテゴリ'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    name = models.CharField('タグ名', max_length=255)
    slug = models.SlugField('URLスラッグ', unique=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'タグ'
        verbose_name_plural = 'タグ'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', '下書き'),
        ('published', '公開'),
    )

    title = models.CharField('タイトル', max_length=255)
    slug = models.SlugField('URLスラッグ', unique=True)
    content = MarkdownxField('本文（Markdown）', blank=True)
    content_rich = RichTextUploadingField('本文（リッチエディタ）', blank=True, config_name='default')
    featured_image = models.ImageField('アイキャッチ画像', upload_to='blog/images/%Y/%m/%d/', blank=True, null=True)
    excerpt = models.TextField('抜粋', blank=True)
    category = models.ForeignKey(Category, verbose_name='カテゴリ', on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, verbose_name='タグ', blank=True)
    status = models.CharField('ステータス', max_length=10, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField('公開日時', null=True, blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = '記事'
        verbose_name_plural = '記事'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def formatted_markdown(self):
        return markdownify(self.content)
    
    @property
    def get_content(self):
        """リッチエディタの内容があればそれを、なければMarkdownを返す"""
        if self.content_rich.strip():
            return self.content_rich
        return self.formatted_markdown
