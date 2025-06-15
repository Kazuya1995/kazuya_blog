#!/usr/bin/env python
"""
データエクスポートスクリプト
開発環境のデータを本番環境に移行するためのスクリプト
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def export_quiz_data():
    """クイズデータをエクスポート"""
    print("クイズデータをエクスポートしています...")
    
    # クイズ関連のデータをエクスポート
    apps_to_export = [
        'quiz.ListeningQuestion',
        'quiz.GrammarQuestion', 
        'quiz.VocabularyQuestion',
        'quiz.UserProgress',
        'quiz.DailyMission',
        'quiz.UserStats'
    ]
    
    for app_model in apps_to_export:
        try:
            output_file = f"{app_model.replace('.', '_').lower()}_data.json"
            execute_from_command_line([
                'manage.py', 'dumpdata', app_model, 
                '--output', output_file, '--indent', '2'
            ])
            print(f"✓ {app_model} データを {output_file} にエクスポートしました")
        except Exception as e:
            print(f"✗ {app_model} のエクスポートに失敗: {e}")

def export_user_data():
    """ユーザーデータをエクスポート（オプション）"""
    print("\nユーザーデータをエクスポートしています...")
    
    try:
        execute_from_command_line([
            'manage.py', 'dumpdata', 'auth.User',
            '--output', 'users_data.json', '--indent', '2'
        ])
        print("✓ ユーザーデータを users_data.json にエクスポートしました")
    except Exception as e:
        print(f"✗ ユーザーデータのエクスポートに失敗: {e}")

def export_time_tracker_data():
    """時間管理アプリのデータをエクスポート"""
    print("\n時間管理データをエクスポートしています...")
    
    time_tracker_models = [
        'time_tracker.Task',
        'time_tracker.TimeLog'
    ]
    
    for app_model in time_tracker_models:
        try:
            output_file = f"{app_model.replace('.', '_').lower()}_data.json"
            execute_from_command_line([
                'manage.py', 'dumpdata', app_model,
                '--output', output_file, '--indent', '2'
            ])
            print(f"✓ {app_model} データを {output_file} にエクスポートしました")
        except Exception as e:
            print(f"✗ {app_model} のエクスポートに失敗: {e}")

def main():
    """メイン実行関数"""
    # Django設定
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
    django.setup()
    
    print("=== データエクスポート開始 ===")
    print("本番環境への移行用データをエクスポートします\n")
    
    # データエクスポート実行
    export_quiz_data()
    export_time_tracker_data()
    
    # ユーザーデータのエクスポート確認
    export_users = input("\nユーザーデータもエクスポートしますか？ (y/N): ")
    if export_users.lower() in ['y', 'yes']:
        export_user_data()
    
    print("\n=== エクスポート完了 ===")
    print("\n次のステップ:")
    print("1. エクスポートされたJSONファイルを本番サーバーにアップロード")
    print("2. 本番環境で以下のコマンドを実行:")
    print("   python manage.py loaddata *.json")
    print("\n注意: 本番環境では既存データが上書きされる可能性があります")

if __name__ == '__main__':
    main()