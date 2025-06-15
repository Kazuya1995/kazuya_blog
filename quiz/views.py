from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
import random
from .models import (
    Vocabulary, GrammarQuestion, ListeningQuestion,
    UserProgress, QuizResult, DailyMission
)
from .tts_service import tts_service


class QuizDashboardView(LoginRequiredMixin, ListView):
    """クイズダッシュボード"""
    template_name = 'quiz/dashboard.html'
    context_object_name = 'recent_results'
    
    def get_queryset(self):
        return QuizResult.objects.filter(user=self.request.user)[:10]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # ユーザー進捗を取得または作成
        progress, created = UserProgress.objects.get_or_create(user=user)
        context['progress'] = progress
        
        # 今日のミッションを取得または作成
        today = timezone.now().date()
        daily_mission, created = DailyMission.objects.get_or_create(
            user=user,
            date=today
        )
        context['daily_mission'] = daily_mission
        
        # 統計情報
        context['total_vocabulary'] = Vocabulary.objects.count()
        context['total_grammar'] = GrammarQuestion.objects.count()
        context['total_listening'] = ListeningQuestion.objects.count()
        
        return context


@login_required
def vocabulary_quiz(request):
    """単語クイズ"""
    # ランダムに単語を選択
    vocabulary = Vocabulary.objects.order_by('?').first()
    
    if not vocabulary:
        messages.error(request, '単語データがありません。')
        return redirect('quiz:dashboard')
    
    # 選択肢を生成（正解 + ランダムな3つの不正解）
    correct_answer = vocabulary.meaning_jp
    wrong_answers = list(Vocabulary.objects.exclude(id=vocabulary.id).values_list('meaning_jp', flat=True))
    random.shuffle(wrong_answers)
    wrong_answers = wrong_answers[:3]
    
    choices = [correct_answer] + wrong_answers
    random.shuffle(choices)
    
    # 正解の選択肢番号を特定
    correct_choice = chr(65 + choices.index(correct_answer))  # A, B, C, D
    
    context = {
        'vocabulary': vocabulary,
        'choices': {
            'A': choices[0],
            'B': choices[1],
            'C': choices[2],
            'D': choices[3],
        },
        'correct_choice': correct_choice,
    }
    
    return render(request, 'quiz/vocabulary_quiz.html', context)


@login_required
def grammar_quiz(request):
    """文法クイズ"""
    # ランダムに文法問題を選択
    grammar_question = GrammarQuestion.objects.order_by('?').first()
    
    if not grammar_question:
        messages.error(request, '文法問題データがありません。')
        return redirect('quiz:dashboard')
    
    context = {
        'question': grammar_question,
    }
    
    return render(request, 'quiz/grammar_quiz.html', context)


@login_required
def listening_quiz(request):
    """リスニングクイズ"""
    # ランダムにリスニング問題を選択
    listening_question = ListeningQuestion.objects.order_by('?').first()
    
    if not listening_question:
        messages.error(request, 'リスニング問題データがありません。')
        return redirect('quiz:dashboard')
    
    context = {
        'question': listening_question,
    }
    
    return render(request, 'quiz/listening_quiz.html', context)


@login_required
def generate_audio(request, question_id):
    """リスニング問題の音声を配信（事前生成ファイル優先）"""
    try:
        listening_question = get_object_or_404(ListeningQuestion, id=question_id)
        
        # 事前生成された音声ファイルが存在する場合はそれを使用
        if listening_question.audio_file and listening_question.audio_file.name:
            try:
                with listening_question.audio_file.open('rb') as audio_file:
                    audio_content = audio_file.read()
                    response = HttpResponse(audio_content, content_type='audio/wav')
                    response['Content-Disposition'] = f'inline; filename="listening_{question_id}.wav"'
                    return response
            except Exception as file_error:
                # ファイル読み込みエラーの場合はリアルタイム生成にフォールバック
                print(f"Audio file read error: {file_error}")
        
        # 事前生成ファイルが存在しない場合はリアルタイム生成
        audio_content = tts_service.synthesize_speech(
            text=listening_question.audio_text,
            language_code='en-US',
            voice_name='en-US-Wavenet-D'  # 自然な男性の声
        )
        
        if audio_content:
            response = HttpResponse(audio_content, content_type='audio/wav')
            response['Content-Disposition'] = f'inline; filename="listening_{question_id}.wav"'
            return response
        else:
            return JsonResponse({'error': 'Failed to generate audio'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def submit_answer(request):
    """回答送信処理"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    quiz_type = request.POST.get('quiz_type')
    question_id = request.POST.get('question_id')
    user_answer = request.POST.get('answer')
    
    if not all([quiz_type, question_id, user_answer]):
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    
    # 正解を確認
    is_correct = False
    correct_answer = ''
    explanation = ''
    
    if quiz_type == 'vocabulary':
        vocabulary = get_object_or_404(Vocabulary, id=question_id)
        # 単語クイズの場合、正解は意味
        correct_answer = request.POST.get('correct_choice', '')
        is_correct = user_answer == correct_answer
        explanation = f'正解: {vocabulary.meaning_jp}\n例文: {vocabulary.example}'
        
    elif quiz_type == 'grammar':
        grammar_question = get_object_or_404(GrammarQuestion, id=question_id)
        correct_answer = grammar_question.correct
        is_correct = user_answer == correct_answer
        explanation = grammar_question.explanation or '解説はありません。'
        
    elif quiz_type == 'listening':
        listening_question = get_object_or_404(ListeningQuestion, id=question_id)
        correct_answer = listening_question.correct
        is_correct = user_answer == correct_answer
        explanation = listening_question.explanation or '音声をもう一度聞いて確認してください。'
    
    # 結果を保存
    QuizResult.objects.create(
        user=request.user,
        quiz_type=quiz_type,
        question_id=question_id,
        user_answer=user_answer,
        is_correct=is_correct
    )
    
    # ユーザー進捗を更新
    progress, created = UserProgress.objects.get_or_create(user=request.user)
    
    if is_correct:
        if quiz_type == 'vocabulary':
            vocabulary = Vocabulary.objects.get(id=question_id)
            progress.vocabulary_completed.add(vocabulary)
        elif quiz_type == 'grammar':
            grammar_question = GrammarQuestion.objects.get(id=question_id)
            progress.grammar_completed.add(grammar_question)
        elif quiz_type == 'listening':
            listening_question = ListeningQuestion.objects.get(id=question_id)
            progress.listening_completed.add(listening_question)
        
        progress.total_score += 10  # 正解で10点
        progress.save()
        
        # 今日のミッションを更新
        today = timezone.now().date()
        daily_mission, created = DailyMission.objects.get_or_create(
            user=request.user,
            date=today
        )
        
        if quiz_type == 'vocabulary':
            daily_mission.vocabulary_completed += 1
        elif quiz_type == 'grammar':
            daily_mission.grammar_completed += 1
        elif quiz_type == 'listening':
            daily_mission.listening_completed += 1
        
        # ミッション完了チェック
        if (daily_mission.vocabulary_completed >= daily_mission.vocabulary_target and
            daily_mission.grammar_completed >= daily_mission.grammar_target and
            daily_mission.listening_completed >= daily_mission.listening_target):
            daily_mission.is_completed = True
        
        daily_mission.save()
    
    return JsonResponse({
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'explanation': explanation,
        'score': progress.total_score,
    })


class ProgressView(LoginRequiredMixin, DetailView):
    """学習進捗表示"""
    model = UserProgress
    template_name = 'quiz/progress.html'
    context_object_name = 'progress'
    
    def get_object(self):
        progress, created = UserProgress.objects.get_or_create(user=self.request.user)
        return progress
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 最近の結果
        context['recent_results'] = QuizResult.objects.filter(
            user=self.request.user
        ).order_by('-answered_at')[:20]
        
        # 今週のミッション履歴
        today = timezone.now().date()
        week_start = today - timezone.timedelta(days=today.weekday())
        context['weekly_missions'] = DailyMission.objects.filter(
            user=self.request.user,
            date__gte=week_start
        ).order_by('-date')
        
        return context
