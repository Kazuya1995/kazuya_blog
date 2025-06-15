#!/usr/bin/env python
"""
TOEIC学習アプリのサンプルデータ作成スクリプト
"""

import os
import sys
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.contrib.auth.models import User
from quiz.models import Vocabulary, GrammarQuestion, ListeningQuestion

def create_sample_data():
    print("TOEIC学習アプリのサンプルデータを作成中...")
    
    # 単語データ
    vocabulary_data = [
        {
            'word': 'accomplish',
            'pronunciation': '/əˈkʌmplɪʃ/',
            'meaning_jp': '達成する、成し遂げる',
            'part_of_speech': 'verb',
            'example': 'We need to accomplish this task by Friday.',
            'difficulty': 'intermediate'
        },
        {
            'word': 'efficient',
            'pronunciation': '/ɪˈfɪʃənt/',
            'meaning_jp': '効率的な',
            'part_of_speech': 'adjective',
            'example': 'This new system is more efficient than the old one.',
            'difficulty': 'intermediate'
        },
        {
            'word': 'revenue',
            'pronunciation': '/ˈrevənjuː/',
            'meaning_jp': '収益、歳入',
            'part_of_speech': 'noun',
            'example': 'The company\'s revenue increased by 15% this year.',
            'difficulty': 'advanced'
        },
        {
            'word': 'negotiate',
            'pronunciation': '/nɪˈɡoʊʃieɪt/',
            'meaning_jp': '交渉する',
            'part_of_speech': 'verb',
            'example': 'We need to negotiate the terms of the contract.',
            'difficulty': 'intermediate'
        },
        {
            'word': 'schedule',
            'pronunciation': '/ˈskedʒuːl/',
            'meaning_jp': 'スケジュール、予定',
            'part_of_speech': 'noun',
            'example': 'Please check your schedule for next week.',
            'difficulty': 'beginner'
        },
        {
            'word': 'conference',
            'pronunciation': '/ˈkɑːnfərəns/',
            'meaning_jp': '会議、協議会',
            'part_of_speech': 'noun',
            'example': 'The annual conference will be held in Tokyo.',
            'difficulty': 'beginner'
        },
        {
            'word': 'implement',
            'pronunciation': '/ˈɪmplɪment/',
            'meaning_jp': '実施する、実行する',
            'part_of_speech': 'verb',
            'example': 'We will implement the new policy next month.',
            'difficulty': 'intermediate'
        },
        {
            'word': 'budget',
            'pronunciation': '/ˈbʌdʒɪt/',
            'meaning_jp': '予算',
            'part_of_speech': 'noun',
            'example': 'The project exceeded its budget.',
            'difficulty': 'beginner'
        }
    ]
    
    # 文法問題データ
    grammar_data = [
        {
            'question': 'The meeting has been _____ until next Friday.',
            'choice_a': 'postponed',
            'choice_b': 'postpone',
            'choice_c': 'postponing',
            'choice_d': 'to postpone',
            'correct': 'A',
            'explanation': '受動態の現在完了形です。「has been + 過去分詞」の形になります。',
            'difficulty': 'intermediate'
        },
        {
            'question': 'Please _____ me know if you need any assistance.',
            'choice_a': 'let',
            'choice_b': 'make',
            'choice_c': 'have',
            'choice_d': 'get',
            'correct': 'A',
            'explanation': '「let someone know」は「〜に知らせる」という意味の熟語です。',
            'difficulty': 'beginner'
        },
        {
            'question': 'The report must be submitted _____ the end of this week.',
            'choice_a': 'by',
            'choice_b': 'until',
            'choice_c': 'at',
            'choice_d': 'in',
            'correct': 'A',
            'explanation': '「by」は期限を表す前置詞で、「〜までに」という意味です。',
            'difficulty': 'intermediate'
        },
        {
            'question': 'She is _____ experienced manager in our department.',
            'choice_a': 'the most',
            'choice_b': 'more',
            'choice_c': 'most',
            'choice_d': 'much',
            'correct': 'A',
            'explanation': '最上級の形です。「the most + 形容詞」で最上級を表します。',
            'difficulty': 'beginner'
        },
        {
            'question': 'The new software will _____ our productivity significantly.',
            'choice_a': 'improve',
            'choice_b': 'improvement',
            'choice_c': 'improving',
            'choice_d': 'improved',
            'correct': 'A',
            'explanation': '助動詞「will」の後には動詞の原形が来ます。',
            'difficulty': 'beginner'
        }
    ]
    
    # リスニング問題データ
    listening_data = [
        {
            'audio_text': 'Good morning, this is Sarah from the marketing department. I\'m calling to confirm our meeting scheduled for tomorrow at 2 PM.',
            'question': 'What is the purpose of this call?',
            'choice_a': 'To schedule a new meeting',
            'choice_b': 'To confirm an existing meeting',
            'choice_c': 'To cancel a meeting',
            'choice_d': 'To change the meeting time',
            'correct': 'B',
            'difficulty': 'beginner'
        },
        {
            'audio_text': 'Attention passengers, flight 245 to New York has been delayed by 30 minutes due to weather conditions. The new departure time is 3:45 PM.',
            'question': 'Why has the flight been delayed?',
            'choice_a': 'Technical problems',
            'choice_b': 'Weather conditions',
            'choice_c': 'Security issues',
            'choice_d': 'Air traffic control',
            'correct': 'B',
            'difficulty': 'intermediate'
        },
        {
            'audio_text': 'Thank you for calling TechSupport. All our representatives are currently busy helping other customers. Your estimated wait time is 5 minutes.',
            'question': 'What is the caller being told?',
            'choice_a': 'The office is closed',
            'choice_b': 'They need to call back later',
            'choice_c': 'They need to wait 5 minutes',
            'choice_d': 'Their call cannot be answered',
            'correct': 'C',
            'difficulty': 'beginner'
        },
        {
            'audio_text': 'The quarterly sales report shows a 12% increase compared to last quarter. This growth is primarily due to our new product line and improved customer service.',
            'question': 'What contributed to the sales increase?',
            'choice_a': 'Lower prices',
            'choice_b': 'New product line and better service',
            'choice_c': 'More advertising',
            'choice_d': 'Seasonal factors',
            'correct': 'B',
            'difficulty': 'intermediate'
        }
    ]
    
    # データベースに保存
    print("単語データを作成中...")
    for vocab_item in vocabulary_data:
        vocabulary, created = Vocabulary.objects.get_or_create(
            word=vocab_item['word'],
            defaults=vocab_item
        )
        if created:
            print(f"  - {vocabulary.word} を作成しました")
        else:
            print(f"  - {vocabulary.word} は既に存在します")
    
    print("\n文法問題データを作成中...")
    for grammar_item in grammar_data:
        grammar, created = GrammarQuestion.objects.get_or_create(
            question=grammar_item['question'],
            defaults=grammar_item
        )
        if created:
            print(f"  - 文法問題を作成しました: {grammar.question[:50]}...")
        else:
            print(f"  - 文法問題は既に存在します: {grammar.question[:50]}...")
    
    print("\nリスニング問題データを作成中...")
    for listening_item in listening_data:
        listening, created = ListeningQuestion.objects.get_or_create(
            audio_text=listening_item['audio_text'],
            defaults=listening_item
        )
        if created:
            print(f"  - リスニング問題を作成しました: {listening.question[:50]}...")
        else:
            print(f"  - リスニング問題は既に存在します: {listening.question[:50]}...")
    
    print("\n✅ サンプルデータの作成が完了しました！")
    print(f"\n📊 作成されたデータ:")
    print(f"  - 単語: {Vocabulary.objects.count()}件")
    print(f"  - 文法問題: {GrammarQuestion.objects.count()}件")
    print(f"  - リスニング問題: {ListeningQuestion.objects.count()}件")
    print("\n🚀 http://127.0.0.1:8000/quiz/ でアプリを確認してください！")

if __name__ == '__main__':
    create_sample_data()