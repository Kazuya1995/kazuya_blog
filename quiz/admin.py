from django.contrib import admin
from .models import (
    Vocabulary, GrammarQuestion, ListeningQuestion,
    UserProgress, QuizResult, DailyMission
)


@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    """単語管理"""
    list_display = ['word', 'part_of_speech', 'meaning_jp', 'created_at']
    list_filter = ['part_of_speech', 'created_at']
    search_fields = ['word', 'meaning_jp']
    ordering = ['id']


@admin.register(GrammarQuestion)
class GrammarQuestionAdmin(admin.ModelAdmin):
    """文法問題管理"""
    list_display = ['grammar', 'question_preview', 'correct', 'created_at']
    list_filter = ['grammar', 'correct', 'created_at']
    search_fields = ['question']
    ordering = ['grammar', 'id']
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = '問題文（プレビュー）'


@admin.register(ListeningQuestion)
class ListeningQuestionAdmin(admin.ModelAdmin):
    """リスニング問題管理"""
    list_display = ['id', 'question_preview', 'correct', 'audio_file', 'created_at']
    list_filter = ['correct', 'created_at']
    search_fields = ['question']
    ordering = ['id']
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = '問題文（プレビュー）'


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    """ユーザー進捗管理"""
    list_display = ['user', 'study_day', 'total_score', 'vocab_progress', 'grammar_progress', 'listening_progress', 'updated_at']
    list_filter = ['study_day', 'created_at']
    search_fields = ['user__username']
    ordering = ['-updated_at']
    
    def vocab_progress(self, obj):
        return f'{obj.vocabulary_progress_percentage}%'
    vocab_progress.short_description = '単語進捗'
    
    def grammar_progress(self, obj):
        return f'{obj.grammar_progress_percentage}%'
    grammar_progress.short_description = '文法進捗'
    
    def listening_progress(self, obj):
        return f'{obj.listening_progress_percentage}%'
    listening_progress.short_description = 'リスニング進捗'


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    """クイズ結果管理"""
    list_display = ['user', 'quiz_type', 'question_id', 'user_answer', 'is_correct', 'answered_at']
    list_filter = ['quiz_type', 'is_correct', 'answered_at']
    search_fields = ['user__username']
    ordering = ['-answered_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編集時は全フィールドを読み取り専用
            return ['user', 'quiz_type', 'question_id', 'user_answer', 'is_correct', 'answered_at']
        return []


@admin.register(DailyMission)
class DailyMissionAdmin(admin.ModelAdmin):
    """日次ミッション管理"""
    list_display = ['user', 'date', 'completion_rate', 'is_completed', 'updated_at']
    list_filter = ['is_completed', 'date']
    search_fields = ['user__username']
    ordering = ['-date']
    
    def completion_rate(self, obj):
        return f'{obj.completion_percentage}%'
    completion_rate.short_description = '完了率'
