from django.urls import path
from . import views

app_name = 'time_tracker'

urlpatterns = [
    # ダッシュボード
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # タスク管理
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    
    # タスク実行
    path('tasks/<int:pk>/start/', views.start_task, name='start_task'),
    path('tasks/<int:pk>/stop/', views.stop_task, name='stop_task'),
    
    # カテゴリ管理
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # 実行ログ
    path('logs/', views.ExecutionLogListView.as_view(), name='log_list'),
    path('logs/<int:pk>/', views.ExecutionLogDetailView.as_view(), name='log_detail'),
    path('logs/<int:pk>/edit/', views.ExecutionLogUpdateView.as_view(), name='log_update'),
    
    # HTMX用API
    path('htmx/current-task/', views.current_task_status, name='current_task_status'),
    path('htmx/timeline/', views.timeline_view, name='timeline_view'),
    path('htmx/stats/', views.stats_view, name='stats_view'),
]