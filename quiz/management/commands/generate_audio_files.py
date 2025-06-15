from django.core.management.base import BaseCommand
from quiz.models import ListeningQuestion
from quiz.tts_service import tts_service


class Command(BaseCommand):
    help = '既存のリスニング問題に音声ファイルを生成します'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='既存の音声ファイルがある場合も強制的に再生成します',
        )
        parser.add_argument(
            '--question-id',
            type=int,
            help='特定の問題IDのみ処理します',
        )
    
    def handle(self, *args, **options):
        force = options['force']
        question_id = options.get('question_id')
        
        # 対象の問題を取得
        if question_id:
            questions = ListeningQuestion.objects.filter(id=question_id)
            if not questions.exists():
                self.stdout.write(
                    self.style.ERROR(f'問題ID {question_id} が見つかりません')
                )
                return
        else:
            questions = ListeningQuestion.objects.all()
        
        total_count = questions.count()
        self.stdout.write(f'対象問題数: {total_count}')
        
        success_count = 0
        error_count = 0
        
        for question in questions:
            # 音声ファイルが既に存在し、強制フラグがない場合はスキップ
            if question.audio_file and question.audio_file.name and not force:
                self.stdout.write(
                    f'問題ID {question.id}: 音声ファイルが既に存在します（スキップ）'
                )
                continue
            
            try:
                # 音声ファイルを生成
                audio_content_file = tts_service.create_audio_file(
                    text=question.audio_text,
                    filename_prefix=f'listening_{question.id}'
                )
                
                if audio_content_file:
                    # 既存のファイルがある場合は削除
                    if question.audio_file:
                        question.audio_file.delete(save=False)
                    
                    # 新しい音声ファイルを保存
                    question.audio_file.save(
                        audio_content_file.name,
                        audio_content_file,
                        save=False
                    )
                    question.save(update_fields=['audio_file'])
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'問題ID {question.id}: 音声ファイルを生成しました'
                        )
                    )
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'問題ID {question.id}: 音声ファイルの生成に失敗しました'
                        )
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'問題ID {question.id}: エラーが発生しました - {str(e)}'
                    )
                )
                error_count += 1
        
        # 結果サマリー
        self.stdout.write('\n=== 処理結果 ===')
        self.stdout.write(f'成功: {success_count}件')
        self.stdout.write(f'エラー: {error_count}件')
        self.stdout.write(f'合計: {total_count}件')
        
        if error_count == 0:
            self.stdout.write(
                self.style.SUCCESS('すべての音声ファイル生成が完了しました！')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'{error_count}件のエラーがありました')
            )