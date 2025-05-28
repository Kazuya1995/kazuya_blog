# Django Technical Blog

技術ブログを運営するためのDjangoプロジェクトです。マークダウンでの記事作成、カテゴリー/タグ管理、コードブロックのシンタックスハイライトなどの機能を備えています。

## 機能

- マークダウンによる記事作成（django-markdownx）
- カテゴリーとタグによる記事管理
- コードブロックのシンタックスハイライト
- レスポンシブデザイン
- 管理画面からの簡単な記事管理

## 必要要件

- Python 3.8以上
- PostgreSQL（本番環境）
- nginx
- gunicorn

## ローカル開発環境のセットアップ

1. リポジトリのクローン:
```bash
git clone https://github.com/yourusername/django-tech-blog.git
cd django-tech-blog
```

2. 仮想環境の作成と有効化:
```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
venv\Scripts\activate     # Windowsの場合
```

3. 依存パッケージのインストール:
```bash
pip install -r requirements.txt
```

4. データベースのマイグレーション:
```bash
python manage.py migrate
```

5. 開発サーバーの起動:
```bash
python manage.py runserver
```

## 本番環境へのデプロイ

1. Ubuntuサーバーの準備:
```bash
sudo apt update
sudo apt upgrade
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib
```

2. PostgreSQLのセットアップ:
```bash
sudo -u postgres psql
CREATE DATABASE your_db_name;
CREATE USER your_db_user WITH PASSWORD 'your_password';
ALTER ROLE your_db_user SET client_encoding TO 'utf8';
ALTER ROLE your_db_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_db_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_db_user;
\q
```

3. プロジェクトのクローンとセットアップ:
```bash
git clone https://github.com/yourusername/django-tech-blog.git
cd django-tech-blog
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. 環境変数の設定:
```bash
# .envファイルを作成し、以下の変数を設定
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

5. 静的ファイルの収集とデータベースのマイグレーション:
```bash
python manage.py collectstatic
python manage.py migrate
```

6. Gunicornの設定:
```bash
# /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/path/to/your/django-tech-blog
ExecStart=/path/to/your/django-tech-blog/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

7. Nginxの設定:
```nginx
# /etc/nginx/sites-available/django-tech-blog
server {
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/your/django-tech-blog;
    }

    location /media/ {
        root /path/to/your/django-tech-blog;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

8. サービスの起動:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo ln -s /etc/nginx/sites-available/django-tech-blog /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

9. SSL証明書の設定（Let's Encrypt）:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## セキュリティに関する注意

- 本番環境では必ず`DEBUG=False`に設定してください
- `SECRET_KEY`は必ず変更し、環境変数として管理してください
- データベースのパスワードは強力なものを使用してください
- 定期的にパッケージのアップデートを行ってください

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。 