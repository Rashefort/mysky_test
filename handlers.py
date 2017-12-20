#!/usr/bin/python3
import json
import datetime
# import tornado.log
from tornado import web
# import dicttoxml
# from tornado.httpclient import AsyncHTTPClient
# import tornado.websocket
# from tornado.concurrent import run_on_executor
import concurrent.futures
from tornado import gen
# from tornado.queues import Queue
# from tornado.escape import json_encode
# from tornado.escape import json_decode
import database
import settings
from settings import logger


executor = concurrent.futures.ProcessPoolExecutor(settings.MAX_POOL_EXECUTORS)


class BaseHandler(web.RequestHandler):
    current_user = ''

    def get_current_user(self):
        return self.get_secure_cookie("mysky_user")


class Main(BaseHandler):
    CONTENT_TYPES = ('documents/pdf', )
    async def get(self):
        files_list = await database.get_files_list()
        logger.debug(f'{files_list}')
        self.render('main.html',
                    title='Полка pdf',
                    options={'files_list': files_list,
                             'current_user': self.current_user}, )

    @web.authenticated
    async def post(self):
        for field_name, files in self.request.files.items():
            for info in files:
                filename, content_type = info['filename'], info['content_type']
                body = info['body']
                logger.info(f'POSTed {field_name} «{filename}» {content_type} {len(body)} bytes')
                # await database.save_pdf(filename, body, self.current_user)
                # gen.Task(database.save_pdf, filename, body,
                # self.current_user, callback=database.save_pdf_completed)
                executor.submit(database.save_pdf, filename, body,
                                self.current_user,
                                callback=database.save_pdf_completed)
        self.write('OK')


class REST(BaseHandler):
    SUPPORTED_METHODS = ('delete',)
    async def delete(self):
        pass


class Login(BaseHandler):
    async def get(self):
        self.render('login.html', title='Введите логин и пароль',
                    # options={'users': await database.get_users()}
                    )

    async def post(self):
        user_name = self.get_argument('user_name')
        user_password = self.get_argument('password')
        auth_user = await database.auth_user(user_name, user_password)
        if (auth_user):
            self.set_secure_cookie("mysky_user", user_name.encode())
            self.current_user = user_name
            self.redirect('/login')
        else:
            self.redirect('/')


class Logout(BaseHandler):
    @web.authenticated
    async def get(self):
        self.clear_cookie("mysky_user")
        self.redirect('/login')
