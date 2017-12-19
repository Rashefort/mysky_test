#!/usr/bin/python3
import os
import logger as logger_

APP_PATH = os.path.dirname(__file__)
SQL_PATH = os.path.join(APP_PATH, 'sql')
MEDIA = os.path.join(APP_PATH, 'media')
MEDIA_PDF = os.path.join(MEDIA, 'pdf')
MEDIA_PAGES = os. path.join(MEDIA_PDF, 'pages')
DB_PATH = os.path.join(APP_PATH, 'database.db')
SQL_ECHO = True
logger = logger_.rotating_log(os.path.join(APP_PATH, 'mysky.log'))

settings = {
    'cookie_secret': '61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=',
    'login_url': '/login',
    'xsrf_cookies': True,
    'debug': True,
    'autoreload': True,
    'compiled_template_cache': False,
    'serve_traceback': True,
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), "templates"),
    'archive_path': os.path.join(os.path.dirname(__file__), 'media'),
}
SERVICE = {'port': 8088, 'address': '0.0.0.0'}
