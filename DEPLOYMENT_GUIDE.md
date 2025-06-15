# 本番環境デプロイガイド

## 概要
TOEICクイズアプリケーションと時間管理アプリを含むDjangoプロジェクトの本番環境デプロイ手順です。

## 前提条件
- Ubuntu 20.04以上のサーバー
- Python 3.8以上
- PostgreSQL
- nginx
- ドメイン名（SSL証明書用）

## 1. サーバーの準備

### システムパッケージの更新
```bash
sudo apt update
sudo apt upgrade -y
```

### 必要パッケージのインストール
```bash
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib git
```

## 2. PostgreSQLの設定

### データベースとユーザーの作成
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE toeic_quiz_db;
CREATE USER toeic_user WITH PASSWORD 'your_strong_password';
ALTER ROLE toeic_user SET client_encoding TO 'utf8';
ALTER ROLE toeic_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE toeic_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE toeic_quiz_db TO toeic_user;
\q
```

## 3. プロジェクトのデプロイ

### リポジトリのクローン
```bash
cd /var/www/
sudo git clone https://github.com/Kazuya1995/kazuya_blog.git
sudo chown -R $USER:$USER kazuya_blog
cd kazuya_blog
```

### 仮想環境の作成
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 環境変数の設定
```bash
sudo nano .env
```

```env
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=your-very-long-secret-key-here
DJANGO_DEBUG=False
DB_NAME=toeic_quiz_db
DB_USER=toeic_user
DB_PASSWORD=your_strong_password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### データベースのマイグレーション
```bash
python manage.py migrate
```

### 静的ファイルの収集
```bash
python manage.py collectstatic --noinput
```

### 問題データのインポート
```bash
python manage.py loaddata quiz_data.json
```

### スーパーユーザーの作成
```bash
python manage.py createsuperuser
```

## 4. Gunicornの設定

### Gunicornサービスファイルの作成
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/kazuya_blog
Environment="PATH=/var/www/kazuya_blog/venv/bin"
ExecStart=/var/www/kazuya_blog/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### Gunicornソケットファイルの作成
```bash
sudo nano /etc/systemd/system/gunicorn.socket
```

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock
SocketUser=www-data
SocketGroup=www-data

[Install]
WantedBy=sockets.target
```

### ファイル権限の設定
```bash
sudo chown -R www-data:www-data /var/www/kazuya_blog
sudo chmod -R 755 /var/www/kazuya_blog
```

### Gunicornサービスの開始
```bash
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl start gunicorn.service
sudo systemctl enable gunicorn.service
```

## 5. Nginxの設定

### サイト設定ファイルの作成
```bash
sudo nano /etc/nginx/sites-available/kazuya_blog
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/kazuya_blog;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        root /var/www/kazuya_blog;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 20M;
}
```

### サイトの有効化
```bash
sudo ln -s /etc/nginx/sites-available/kazuya_blog /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 6. SSL証明書の設定（Let's Encrypt）

### Certbotのインストール
```bash
sudo apt install certbot python3-certbot-nginx
```

### SSL証明書の取得
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 7. セキュリティ設定

### ファイアウォールの設定
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable
```

### 定期的な証明書更新の設定
```bash
sudo crontab -e
```

```cron
0 12 * * * /usr/bin/certbot renew --quiet
```

## 8. 動作確認

1. ブラウザでドメインにアクセス
2. 管理画面（/admin/）にアクセス
3. TOEICクイズ機能の動作確認
4. 時間管理機能の動作確認

## 9. メンテナンス

### ログの確認
```bash
# Gunicornログ
sudo journalctl -u gunicorn.service

# Nginxログ
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### アプリケーションの更新
```bash
cd /var/www/kazuya_blog
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn.service
```

## トラブルシューティング

### よくある問題
1. **502 Bad Gateway**: Gunicornサービスの状態を確認
2. **静的ファイルが表示されない**: collectstaticの実行とNginx設定を確認
3. **データベース接続エラー**: PostgreSQLの設定と環境変数を確認

### ログファイルの場所
- Django: `/var/www/kazuya_blog/logs/`（設定により）
- Gunicorn: `sudo journalctl -u gunicorn.service`
- Nginx: `/var/log/nginx/`
- PostgreSQL: `/var/log/postgresql/`