from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q, Sum, Count
from datetime import datetime, timedelta
from .models import Task, TaskCategory, TaskExecutionLog
from .forms import TaskForm, TaskCategoryForm, TaskExecutionLogForm


class DashboardView(LoginRequiredMixin, ListView):
    """ダッシュボード - メイン画面"""
    template_name = 'time_tracker/dashboard.html'
    context_object_name = 'recent_tasks'
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('-updated_at')[:5]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()
        
        # 現在実行中のタスク
        context['current_task'] = Task.objects.filter(user=user, is_active=True).first()
        
        # 今日の統計
        today_logs = TaskExecutionLog.objects.filter(
            task__user=user,
            start_time__date=today,
            end_time__isnull=False
        )
        context['today_total_time'] = sum(
            [(log.end_time - log.start_time).total_seconds() / 60 for log in today_logs]
        )
        context['today_task_count'] = today_logs.count()
        
        # カテゴリ別統計（今日）
        context['category_stats'] = TaskCategory.objects.filter(
            task__taskexecutionlog__start_time__date=today,
            task__user=user
        ).annotate(
            total_time=Sum('task__taskexecutionlog__actual_minutes')
        ).order_by('-total_time')
        
        return context


class TaskListView(LoginRequiredMixin, ListView):
    """タスク一覧"""
    model = Task
    template_name = 'time_tracker/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('-updated_at')


class TaskDetailView(LoginRequiredMixin, DetailView):
    """タスク詳細"""
    model = Task
    template_name = 'time_tracker/task_detail.html'
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['execution_logs'] = self.object.taskexecutionlog_set.order_by('-start_time')[:10]
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    """タスク作成"""
    model = Task
    form_class = TaskForm
    template_name = 'time_tracker/task_form.html'
    success_url = reverse_lazy('time_tracker:task_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """タスク編集"""
    model = Task
    form_class = TaskForm
    template_name = 'time_tracker/task_form.html'
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """タスク削除"""
    model = Task
    template_name = 'time_tracker/task_confirm_delete.html'
    success_url = reverse_lazy('time_tracker:task_list')
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


@login_required
def start_task(request, pk):
    """タスク開始"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    # 他のタスクが実行中の場合は停止
    current_task = Task.objects.filter(user=request.user, is_active=True).first()
    if current_task and current_task != task:
        stop_task(request, current_task.pk)
    
    # タスクを開始
    task.is_active = True
    task.save()
    
    # 実行ログを作成
    TaskExecutionLog.objects.create(
        task=task,
        start_time=timezone.now()
    )
    
    messages.success(request, f'タスク「{task.title}」を開始しました。')
    
    if request.headers.get('HX-Request'):
        # 開始後の更新されたタスクカードを返す
        return render(request, 'time_tracker/htmx/task_card.html', {
            'task': task
        })
    
    return redirect('time_tracker:dashboard')


@login_required
def stop_task(request, pk):
    """タスク停止"""
    task = get_object_or_404(Task, pk=pk, user=request.user, is_active=True)
    
    # タスクを停止
    task.is_active = False
    task.save()
    
    # 最新の実行ログを終了
    log = TaskExecutionLog.objects.filter(
        task=task,
        end_time__isnull=True
    ).order_by('-start_time').first()
    
    if log:
        log.end_time = timezone.now()
        log.save()
    
    messages.success(request, f'タスク「{task.title}」を停止しました。')
    
    if request.headers.get('HX-Request'):
        # リファラーURLから適切なテンプレートを判定
        referer = request.META.get('HTTP_REFERER', '')
        
        if 'current-task' in referer or 'htmx' in referer:
            # フローティングタイマーからのリクエストの場合
            return render(request, 'time_tracker/htmx/current_task_status.html', {
                'current_task': None
            })
        else:
            # ダッシュボードやタスク一覧からのリクエストの場合、更新されたタスクカードを返す
            return render(request, 'time_tracker/htmx/task_card.html', {
                'task': task
            })
    
    return redirect('time_tracker:dashboard')


class CategoryListView(LoginRequiredMixin, ListView):
    """カテゴリ一覧"""
    model = TaskCategory
    template_name = 'time_tracker/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """カテゴリ作成"""
    model = TaskCategory
    form_class = TaskCategoryForm
    template_name = 'time_tracker/category_form.html'
    success_url = reverse_lazy('time_tracker:category_list')


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """カテゴリ編集"""
    model = TaskCategory
    form_class = TaskCategoryForm
    template_name = 'time_tracker/category_form.html'
    success_url = reverse_lazy('time_tracker:category_list')


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """カテゴリ削除"""
    model = TaskCategory
    template_name = 'time_tracker/category_confirm_delete.html'
    success_url = reverse_lazy('time_tracker:category_list')


class ExecutionLogListView(LoginRequiredMixin, ListView):
    """実行ログ一覧"""
    model = TaskExecutionLog
    template_name = 'time_tracker/log_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    
    def get_queryset(self):
        return TaskExecutionLog.objects.filter(
            task__user=self.request.user
        ).order_by('-start_time')


class ExecutionLogDetailView(LoginRequiredMixin, DetailView):
    """実行ログ詳細"""
    model = TaskExecutionLog
    template_name = 'time_tracker/log_detail.html'
    
    def get_queryset(self):
        return TaskExecutionLog.objects.filter(task__user=self.request.user)


class ExecutionLogUpdateView(LoginRequiredMixin, UpdateView):
    """実行ログ編集"""
    model = TaskExecutionLog
    form_class = TaskExecutionLogForm
    template_name = 'time_tracker/log_form.html'
    
    def get_queryset(self):
        return TaskExecutionLog.objects.filter(task__user=self.request.user)


# HTMX用ビュー
@login_required
def current_task_status(request):
    """現在のタスク状況をHTMX用に返す"""
    current_task = Task.objects.filter(user=request.user, is_active=True).first()
    
    context = {
        'current_task': current_task,
    }
    
    if current_task:
        # 実行時間を計算
        log = TaskExecutionLog.objects.filter(
            task=current_task,
            end_time__isnull=True
        ).order_by('-start_time').first()
        
        if log:
            duration = timezone.now() - log.start_time
            context['duration_seconds'] = int(duration.total_seconds())
    
    return render(request, 'time_tracker/htmx/current_task_status.html', context)


@login_required
def timeline_view(request):
    """タイムライン表示用"""
    date_str = request.GET.get('date', timezone.now().date().isoformat())
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        target_date = timezone.now().date()
    
    logs = TaskExecutionLog.objects.filter(
        task__user=request.user,
        start_time__date=target_date,
        end_time__isnull=False
    ).order_by('start_time')
    
    context = {
        'logs': logs,
        'target_date': target_date,
    }
    
    return render(request, 'time_tracker/htmx/timeline.html', context)


@login_required
def stats_view(request):
    """統計表示用"""
    period = request.GET.get('period', 'week')  # week, month, year
    
    if period == 'week':
        start_date = timezone.now().date() - timedelta(days=7)
    elif period == 'month':
        start_date = timezone.now().date() - timedelta(days=30)
    else:  # year
        start_date = timezone.now().date() - timedelta(days=365)
    
    logs = TaskExecutionLog.objects.filter(
        task__user=request.user,
        start_time__date__gte=start_date,
        end_time__isnull=False
    )
    
    # カテゴリ別統計
    category_stats = {}
    for log in logs:
        category = log.task.category.name if log.task.category else '未分類'
        if category not in category_stats:
            category_stats[category] = 0
        category_stats[category] += log.actual_minutes or 0
    
    context = {
        'category_stats': category_stats,
        'period': period,
        'total_time': sum(category_stats.values()),
    }
    
    return render(request, 'time_tracker/htmx/stats.html', context)
