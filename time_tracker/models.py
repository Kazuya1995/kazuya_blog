from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class TaskCategory(models.Model):
    """タスクカテゴリ（仕事、自己投資、娯楽・休息など）"""
    name = models.CharField('カテゴリ名', max_length=100)
    description = models.TextField('説明', blank=True, help_text='カテゴリの説明（任意）')
    color = models.CharField('色', max_length=7, default='#cccccc', help_text='HEX形式（例: #ff0000）')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'タスクカテゴリ'
        verbose_name_plural = 'タスクカテゴリ'
        ordering = ['name']

    def __str__(self):
        return self.name
    
    @property
    def active_tasks_count(self):
        """実行中のタスク数を返す"""
        return self.task_set.filter(is_active=True).count()


class Task(models.Model):
    """タスク"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザー')
    title = models.CharField('タスク名', max_length=255)
    category = models.ForeignKey(
        TaskCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='カテゴリ'
    )
    estimated_minutes = models.PositiveIntegerField(
        '見積時間（分）', 
        null=True, 
        blank=True,
        help_text='予想される実行時間（分単位）'
    )
    is_active = models.BooleanField('実行中', default=False)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'タスク'
        verbose_name_plural = 'タスク'
        ordering = ['-updated_at']
        constraints = [
            # 1ユーザーにつき同時実行可能なタスクは1つまで
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_active=True),
                name='unique_active_task_per_user'
            )
        ]

    def __str__(self):
        return f'{self.title} ({self.user.username})'

    def get_absolute_url(self):
        return reverse('time_tracker:task_detail', kwargs={'pk': self.pk})

    @property
    def total_execution_time(self):
        """このタスクの総実行時間（分）を返す"""
        total_seconds = 0
        for log in self.taskexecutionlog_set.filter(end_time__isnull=False):
            duration = log.end_time - log.start_time
            total_seconds += duration.total_seconds()
        return int(total_seconds / 60)


class TaskExecutionLog(models.Model):
    """タスク実行ログ"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='タスク')
    start_time = models.DateTimeField('開始時刻')
    end_time = models.DateTimeField('終了時刻', null=True, blank=True)
    actual_minutes = models.PositiveIntegerField(
        '実際の実行時間（分）', 
        null=True, 
        blank=True,
        help_text='自動計算される実行時間'
    )
    notes = models.TextField('メモ', blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'タスク実行ログ'
        verbose_name_plural = 'タスク実行ログ'
        ordering = ['-start_time']

    def __str__(self):
        status = '実行中' if self.end_time is None else '完了'
        return f'{self.task.title} - {self.start_time.strftime("%Y/%m/%d %H:%M")} ({status})'

    def save(self, *args, **kwargs):
        """保存時に実行時間を自動計算"""
        if self.end_time and self.start_time:
            duration = self.end_time - self.start_time
            self.actual_minutes = int(duration.total_seconds() / 60)
        super().save(*args, **kwargs)

    @property
    def duration_display(self):
        """実行時間を表示用フォーマットで返す"""
        if not self.end_time:
            return '実行中'
        
        duration = self.end_time - self.start_time
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f'{hours}時間{minutes}分{seconds}秒'
        elif minutes > 0:
            return f'{minutes}分{seconds}秒'
        else:
            return f'{seconds}秒'

    @property
    def is_running(self):
        """実行中かどうかを返す"""
        return self.end_time is None
