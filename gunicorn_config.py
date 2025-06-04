import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
bind = 'unix:/home/ubuntu/kazuya_blog/gunicorn.sock'
wsgi_app = 'config.wsgi:application'
user = 'ubuntu'
group = 'ubuntu'
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
preload_app = True