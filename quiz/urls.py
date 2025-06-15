from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'quiz'

urlpatterns = [
    # 認証
    path('login/', auth_views.LoginView.as_view(template_name='quiz/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='quiz:login'), name='logout'),
    
    # ダッシュボード
    path('', views.QuizDashboardView.as_view(), name='dashboard'),
    
    # クイズページ
    path('vocabulary/', views.vocabulary_quiz, name='vocabulary_quiz'),
    path('grammar/', views.grammar_quiz, name='grammar_quiz'),
    path('listening/', views.listening_quiz, name='listening_quiz'),
    path('listening/audio/<int:question_id>/', views.generate_audio, name='generate_audio'),
    
    # 回答送信
    path('submit/', views.submit_answer, name='submit_answer'),
    
    # 進捗表示
    path('progress/', views.ProgressView.as_view(), name='progress'),
]