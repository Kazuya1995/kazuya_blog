from django.contrib import admin
from .models import TaskCategory, Task, TaskExecutionLog


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    ordering = ('name',)


class TaskExecutionLogInline(admin.TabularInline):
    model = TaskExecutionLog
    extra = 0
    readonly_fields = ('actual_minutes', 'duration_display')
    fields = ('start_time', 'end_time', 'actual_minutes', 'notes')

    def duration_display(self, obj):
        return obj.duration_display
    duration_display.short_description = '実行時間'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'estimated_minutes', 'is_active', 'total_execution_time', 'updated_at')
    list_filter = ('is_active', 'category', 'created_at', 'user')
    search_fields = ('title', 'user__username')
    ordering = ('-updated_at',)
    inlines = [TaskExecutionLogInline]
    
    def total_execution_time(self, obj):
        return f'{obj.total_execution_time}分'
    total_execution_time.short_description = '総実行時間'


@admin.register(TaskExecutionLog)
class TaskExecutionLogAdmin(admin.ModelAdmin):
    list_display = ('task', 'start_time', 'end_time', 'actual_minutes', 'duration_display', 'is_running')
    list_filter = ('start_time', 'end_time', 'task__category', 'task__user')
    search_fields = ('task__title', 'task__user__username', 'notes')
    ordering = ('-start_time',)
    readonly_fields = ('actual_minutes', 'duration_display')
    
    def duration_display(self, obj):
        return obj.duration_display
    duration_display.short_description = '実行時間'
    
    def is_running(self, obj):
        return obj.is_running
    is_running.short_description = '実行中'
    is_running.boolean = True
