#!/usr/bin/python3
from tornado.web import StaticFileHandler
import handlers
import settings


def routes_setup():
    return [
        (r'/post', handlers.PostFile),
        (r'/login', handlers.Login),
        (r'/logout', handlers.Logout),
        (r'/', handlers.Main),
        (r'/pdf/(?P<hashed_name>[^\/]+)/?(?P<page>[^\/]+)?', handlers.Preview),
        (r'/media/pdf/(?P<hashed_name>[^\/]+)', handlers.PdfFileStreamDownload, {'file_path': settings.MEDIA_PDF}),
        (r'/media/png/(?P<hashed_name>[^\/]+)/?(?P<page>[^\/]+)', handlers.PngFileStreamDownload, {'file_path': settings.MEDIA_PAGES}),
        (r'/pages/(.*)', StaticFileHandler, {'path': f'{settings.MEDIA_PAGES}'}),
        ]
