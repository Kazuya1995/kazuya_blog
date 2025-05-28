from django.core.management.base import BaseCommand
from django.utils import timezone
from blog.models import Category, Tag, Post
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import random
import io
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Creates dummy blog data for testing'

    def create_thumbnail(self, text, width=800, height=400):
        self.stdout.write(f'Creating thumbnail for text: {text}')
        
        # 画像の作成
        image = Image.new('RGB', (width, height), color=self.random_color())
        draw = ImageDraw.Draw(image)

        # ランダムな背景パターンを描画
        for _ in range(10):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill=self.random_color(), width=5)

        # テキストを描画
        text_color = (255, 255, 255)  # 白色
        text_size = 40

        self.stdout.write('Attempting to load font...')
        # フォントの設定
        try:
            # macOSのシステムフォントを使用
            font = ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc', text_size)
            self.stdout.write('Using macOS font')
        except Exception as e:
            self.stdout.write(f'Failed to load macOS font: {str(e)}')
            try:
                # Ubuntuのシステムフォントを使用
                font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', text_size)
                self.stdout.write('Using Ubuntu font')
            except Exception as e:
                self.stdout.write(f'Failed to load Ubuntu font: {str(e)}')
                # それでもダメな場合はデフォルトフォントを使用
                font = ImageFont.load_default()
                self.stdout.write('Using default font')

        # テキストを短く切り詰める（必要な場合）
        if len(text) > 30:
            text = text[:27] + '...'

        # テキストのサイズを計算
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # テキストを中央に配置
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # テキストの背景を描画
        padding = 20
        draw.rectangle(
            [
                (x - padding, y - padding),
                (x + text_width + padding, y + text_height + padding)
            ],
            fill=(0, 0, 0, 128)  # 半透明の黒
        )

        # テキストを描画
        draw.text((x, y), text, font=font, fill=text_color)

        # 画像をバイトストリームに変換
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG', quality=85)
        image_io.seek(0)

        self.stdout.write('Thumbnail created successfully')
        return image_io

    def random_color(self):
        # ある程度落ち着いた色合いにするため、完全なランダムではなく、
        # RGBの各値を50-200の範囲で生成
        return (
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(50, 200)
        )

    def handle(self, *args, **kwargs):
        # メディアディレクトリの作成
        media_root = settings.MEDIA_ROOT
        images_dir = os.path.join(media_root, 'blog', 'images')
        os.makedirs(images_dir, exist_ok=True)
        self.stdout.write(f'Media directory created at: {images_dir}')

        # カテゴリの作成
        categories = [
            {'name': 'テクノロジー', 'slug': 'technology', 'description': '最新のテクノロジーに関する記事'},
            {'name': '旅行', 'slug': 'travel', 'description': '世界各地の旅行記'},
            {'name': 'ライフスタイル', 'slug': 'lifestyle', 'description': '日常生活に関するヒントとアドバイス'},
            {'name': '料理', 'slug': 'cooking', 'description': 'レシピと料理のコツ'},
        ]

        created_categories = []
        for category_data in categories:
            category, created = Category.objects.get_or_create(
                slug=category_data['slug'],
                defaults=category_data
            )
            created_categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # タグの作成
        tags = [
            {'name': 'Python', 'slug': 'python'},
            {'name': 'Django', 'slug': 'django'},
            {'name': '初心者向け', 'slug': 'beginner'},
            {'name': 'プログラミング', 'slug': 'programming'},
            {'name': 'Web開発', 'slug': 'web-development'},
            {'name': '海外旅行', 'slug': 'overseas-travel'},
            {'name': '国内旅行', 'slug': 'domestic-travel'},
            {'name': '節約', 'slug': 'saving-money'},
            {'name': '健康', 'slug': 'health'},
        ]

        created_tags = []
        for tag_data in tags:
            tag, created = Tag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults=tag_data
            )
            created_tags.append(tag)
            if created:
                self.stdout.write(f'Created tag: {tag.name}')

        # 記事の作成
        posts = [
            {
                'title': 'Djangoで始めるWeb開発入門',
                'slug': 'django-web-development-introduction',
                'content': '''
Djangoは、Pythonで書かれた強力なWebフレームワークです。
初心者にも扱いやすく、多くの機能が標準で搭載されています。

## Djangoの特徴
- 管理画面が標準で用意されている
- セキュリティ機能が充実
- 豊富なドキュメント
- 活発なコミュニティ

## 開発の始め方
1. 仮想環境の作成
2. Djangoのインストール
3. プロジェクトの作成
4. アプリケーションの作成

詳しい手順は以下の通りです...
                ''',
                'category': 'technology',
                'tags': ['python', 'django', 'web-development', 'beginner'],
                'status': 'published',
            },
            {
                'title': '京都旅行記：古都の魅力を探る',
                'slug': 'kyoto-travel-guide',
                'content': '''
京都は日本の伝統文化が今も息づく街です。
今回は、京都の隠れた名所をご紹介します。

## おすすめスポット
1. 祇園白川
2. 哲学の道
3. 京都御苑
4. 錦市場

## 観光のコツ
- 早朝観光がおすすめ
- 公共交通機関の活用
- 季節ごとの見どころ
                ''',
                'category': 'travel',
                'tags': ['domestic-travel'],
                'status': 'published',
            },
            {
                'title': '毎日の節約術：無理なく続けるコツ',
                'slug': 'daily-saving-tips',
                'content': '''
節約は継続が大切です。
今回は、無理なく続けられる節約のコツをご紹介します。

## 食費の節約
- 週間メニューの作成
- まとめ買いのコツ
- 食材の使い切り

## 光熱費の節約
- こまめなスイッチオフ
- 季節に合わせた設定
- 効率的な家電の使用
                ''',
                'category': 'lifestyle',
                'tags': ['saving-money'],
                'status': 'published',
            },
            {
                'title': '季節の野菜を使った簡単レシピ',
                'slug': 'seasonal-vegetable-recipes',
                'content': '''
旬の野菜は栄養価が高く、お手頃価格で手に入ります。
今回は、季節の野菜を使った簡単レシピをご紹介します。

## 春野菜のレシピ
- アスパラガスのグリル
- 新玉ねぎのサラダ
- 春キャベツの炒め物

## 保存方法
- 野菜ごとの適切な保存方法
- 長持ちさせるコツ
- 冷凍保存のテクニック
                ''',
                'category': 'cooking',
                'tags': ['health'],
                'status': 'published',
            },
        ]

        # 管理者ユーザーの取得
        admin_user = User.objects.filter(is_superuser=True).first()

        for post_data in posts:
            try:
                self.stdout.write(f'Processing post: {post_data["title"]}')
                
                # カテゴリの取得
                category = Category.objects.get(slug=post_data['category'])
                self.stdout.write(f'Found category: {category.name}')
                
                # 記事の作成
                post, created = Post.objects.get_or_create(
                    slug=post_data['slug'],
                    defaults={
                        'title': post_data['title'],
                        'content': post_data['content'],
                        'category': category,
                        'status': post_data['status'],
                        'published_at': timezone.now(),
                    }
                )

                if created:
                    self.stdout.write(f'Created new post: {post.title}')
                    # サムネイル画像の生成と保存
                    try:
                        self.stdout.write('Generating thumbnail...')
                        image_io = self.create_thumbnail(post.title)
                        
                        self.stdout.write('Saving thumbnail...')
                        filename = f'blog/images/{post.slug}.jpg'
                        post.featured_image.save(filename, ContentFile(image_io.getvalue()), save=True)
                        self.stdout.write(f'Thumbnail saved successfully: {filename}')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating thumbnail for {post.title}: {str(e)}'))

                    # タグの追加
                    for tag_slug in post_data['tags']:
                        tag = Tag.objects.get(slug=tag_slug)
                        post.tags.add(tag)
                        self.stdout.write(f'Added tag: {tag.name}')
                    
                    self.stdout.write(f'Post creation completed: {post.title}')
                else:
                    self.stdout.write(f'Post already exists: {post.title}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing post {post_data["title"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully created dummy data')) 