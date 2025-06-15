#!/usr/bin/env python
import os
import sys
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.contrib.auth.models import User
from time_tracker.models import Task, TaskCategory

# テストユーザーを作成または取得
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com'}
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f'新しいユーザーを作成しました: {user.username}')
else:
    print(f'既存のユーザーを使用します: {user.username}')

# テストカテゴリを作成
category, created = TaskCategory.objects.get_or_create(
    name='テストカテゴリ',
    defaults={'color': '#ff0000', 'description': 'テスト用のカテゴリです'}
)
if created:
    print(f'新しいカテゴリを作成しました: {category.name}')
else:
    print(f'既存のカテゴリを使用します: {category.name}')

# テストタスクを作成
task, created = Task.objects.get_or_create(
    user=user,
    title='テストタスク1',
    defaults={
        'category': category,
        'estimated_minutes': 30
    }
)
if created:
    print(f'新しいタスクを作成しました: {task.title}')
else:
    print(f'既存のタスクを使用します: {task.title}')

# 追加のテストタスクを作成
task2, created = Task.objects.get_or_create(
    user=user,
    title='テストタスク2',
    defaults={
        'category': category,
        'estimated_minutes': 45
    }
)
if created:
    print(f'新しいタスクを作成しました: {task2.title}')
else:
    print(f'既存のタスクを使用します: {task2.title}')

print('\nテストデータの準備が完了しました！')
print(f'ユーザー: {user.username}')
print(f'カテゴリ: {category.name}')
print(f'タスク1: {task.title} (見積: {task.estimated_minutes}分)')
print(f'タスク2: {task2.title} (見積: {task2.estimated_minutes}分)')