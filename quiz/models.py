from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Vocabulary(models.Model):
    """TOEIC単語モデル"""
    DIFFICULTY_CHOICES = [
        ('beginner', '初級'),
        ('intermediate', '中級'),
        ('advanced', '上級'),
    ]
    
    word = models.CharField(max_length=100, verbose_name='単語')
    pronunciation = models.CharField(max_length=100, blank=True, verbose_name='発音')
    part_of_speech = models.CharField(max_length=20, verbose_name='品詞')
    meaning_jp = models.TextField(verbose_name='日本語意味')
    example = models.TextField(verbose_name='例文')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='intermediate', verbose_name='難易度')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'TOEIC単語'
        verbose_name_plural = 'TOEIC単語'
        ordering = ['id']
    
    def __str__(self):
        return f'{self.word} ({self.part_of_speech})'


class GrammarQuestion(models.Model):
    """文法問題モデル"""
    GRAMMAR_CHOICES = [
        ('parts_of_speech', '品詞識別'),
        ('passive_voice', '受動態'),
        ('comparison', '比較表現'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', '初級'),
        ('intermediate', '中級'),
        ('advanced', '上級'),
    ]
    
    grammar = models.CharField(max_length=50, choices=GRAMMAR_CHOICES, verbose_name='文法項目')
    question = models.TextField(verbose_name='問題文')
    choice_a = models.CharField(max_length=200, verbose_name='選択肢A')
    choice_b = models.CharField(max_length=200, verbose_name='選択肢B')
    choice_c = models.CharField(max_length=200, verbose_name='選択肢C')
    choice_d = models.CharField(max_length=200, default='Default choice D', verbose_name='選択肢D')
    correct = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], verbose_name='正解')
    explanation = models.TextField(blank=True, verbose_name='解説')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='intermediate', verbose_name='難易度')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '文法問題'
        verbose_name_plural = '文法問題'
        ordering = ['grammar', 'id']
    
    def __str__(self):
        return f'{self.get_grammar_display()} - {self.question[:50]}...'


class ListeningQuestion(models.Model):
    """リスニング問題モデル（Part 2形式）"""
    DIFFICULTY_CHOICES = [
        ('beginner', '初級'),
        ('intermediate', '中級'),
        ('advanced', '上級'),
    ]
    
    audio_text = models.TextField(default='Sample audio text', verbose_name='音声テキスト')
    question = models.TextField(blank=True, verbose_name='問題文')
    choice_a = models.CharField(max_length=200, verbose_name='選択肢A')
    choice_b = models.CharField(max_length=200, verbose_name='選択肢B')
    choice_c = models.CharField(max_length=200, verbose_name='選択肢C')
    choice_d = models.CharField(max_length=200, default='Default choice D', verbose_name='選択肢D')
    correct = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], verbose_name='正解')
    explanation = models.TextField(blank=True, verbose_name='解説')
    audio_file = models.FileField(upload_to='listening_audio/', blank=True, null=True, verbose_name='音声ファイル')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='intermediate', verbose_name='難易度')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # audio_textの初期値を記録（変更検知用）
        self._original_audio_text = self.audio_text
    
    class Meta:
        verbose_name = 'リスニング問題'
        verbose_name_plural = 'リスニング問題'
        ordering = ['id']
    
    def save(self, *args, **kwargs):
        """保存時に音声ファイルを自動生成"""
        # 新規作成時、または音声ファイルが存在しない場合、またはaudio_textが変更された場合に音声を生成
        audio_text_changed = hasattr(self, '_original_audio_text') and self._original_audio_text != self.audio_text
        should_generate_audio = (
            self.audio_text and (
                self._state.adding or  # 新規作成
                not self.audio_file or  # 音声ファイルが存在しない
                audio_text_changed  # audio_textが変更された
            )
        )
        
        if should_generate_audio:
            from .tts_service import tts_service
            
            # 音声ファイルを生成
            audio_content_file = tts_service.create_audio_file(
                text=self.audio_text,
                filename_prefix=f'listening_{self.id or "new"}'
            )
            
            if audio_content_file:
                # 既存のファイルがある場合は削除
                if self.audio_file:
                    self.audio_file.delete(save=False)
                
                # 新しい音声ファイルを保存
                self.audio_file.save(
                    audio_content_file.name,
                    audio_content_file,
                    save=False
                )
        
        super().save(*args, **kwargs)
        
        # 保存後に現在の値を記録
        self._original_audio_text = self.audio_text
    
    def __str__(self):
        return f'リスニング問題 {self.id} - {self.question[:50]}...'


class UserProgress(models.Model):
    """ユーザーの学習進捗モデル"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザー')
    study_day = models.PositiveIntegerField(default=1, verbose_name='学習日数')
    vocabulary_completed = models.ManyToManyField(Vocabulary, blank=True, verbose_name='完了した単語')
    grammar_completed = models.ManyToManyField(GrammarQuestion, blank=True, verbose_name='完了した文法問題')
    listening_completed = models.ManyToManyField(ListeningQuestion, blank=True, verbose_name='完了したリスニング問題')
    total_score = models.PositiveIntegerField(default=0, verbose_name='総合スコア')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'ユーザー進捗'
        verbose_name_plural = 'ユーザー進捗'
        unique_together = ['user']
    
    def __str__(self):
        return f'{self.user.username} - Day {self.study_day}'
    
    @property
    def vocabulary_progress_percentage(self):
        """単語学習の進捗率"""
        total_vocab = Vocabulary.objects.count()
        if total_vocab == 0:
            return 0
        completed_vocab = self.vocabulary_completed.count()
        return round((completed_vocab / total_vocab) * 100, 1)
    
    @property
    def grammar_progress_percentage(self):
        """文法学習の進捗率"""
        total_grammar = GrammarQuestion.objects.count()
        if total_grammar == 0:
            return 0
        completed_grammar = self.grammar_completed.count()
        return round((completed_grammar / total_grammar) * 100, 1)
    
    @property
    def listening_progress_percentage(self):
        """リスニング学習の進捗率"""
        total_listening = ListeningQuestion.objects.count()
        if total_listening == 0:
            return 0
        completed_listening = self.listening_completed.count()
        return round((completed_listening / total_listening) * 100, 1)


class QuizResult(models.Model):
    """クイズ結果モデル"""
    QUIZ_TYPE_CHOICES = [
        ('vocabulary', '単語'),
        ('grammar', '文法'),
        ('listening', 'リスニング'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザー')
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPE_CHOICES, verbose_name='クイズタイプ')
    question_id = models.PositiveIntegerField(verbose_name='問題ID')
    user_answer = models.CharField(max_length=1, verbose_name='ユーザーの回答')
    is_correct = models.BooleanField(verbose_name='正解フラグ')
    answered_at = models.DateTimeField(default=timezone.now, verbose_name='回答日時')
    
    class Meta:
        verbose_name = 'クイズ結果'
        verbose_name_plural = 'クイズ結果'
        ordering = ['-answered_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_quiz_type_display()} - {"正解" if self.is_correct else "不正解"}'


class DailyMission(models.Model):
    """日次ミッションモデル"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザー')
    date = models.DateField(default=timezone.now, verbose_name='日付')
    vocabulary_target = models.PositiveIntegerField(default=5, verbose_name='単語目標数')
    grammar_target = models.PositiveIntegerField(default=3, verbose_name='文法目標数')
    listening_target = models.PositiveIntegerField(default=1, verbose_name='リスニング目標数')
    vocabulary_completed = models.PositiveIntegerField(default=0, verbose_name='単語完了数')
    grammar_completed = models.PositiveIntegerField(default=0, verbose_name='文法完了数')
    listening_completed = models.PositiveIntegerField(default=0, verbose_name='リスニング完了数')
    is_completed = models.BooleanField(default=False, verbose_name='ミッション完了フラグ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '日次ミッション'
        verbose_name_plural = '日次ミッション'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f'{self.user.username} - {self.date} - {"完了" if self.is_completed else "未完了"}'
    
    @property
    def completion_percentage(self):
        """ミッション完了率"""
        total_target = self.vocabulary_target + self.grammar_target + self.listening_target
        total_completed = self.vocabulary_completed + self.grammar_completed + self.listening_completed
        if total_target == 0:
            return 0
        return round((total_completed / total_target) * 100, 1)
