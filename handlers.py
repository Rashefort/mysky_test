#!/usr/bin/python3
import json
import datetime
import concurrent.futures
from tornado.log import logging
from tornado import web
from tornado.ioloop import IOLoop
from tornado.escape import xhtml_escape
# from tornado.stack_context import run_with_stack_context, NullContext
# import dicttoxml
# from tornado.httpclient import AsyncHTTPClient
# import tornado.websocket
from tornado import gen
# from tornado.queues import Queue
# from tornado.escape import json_encode
# from tornado.escape import json_decode
import pdf_utils as updf
import database
import settings


executor = concurrent.futures.ProcessPoolExecutor(settings.MAX_POOL_EXECUTORS)


class BaseHandler(web.RequestHandler):
    # current_user = 'user'

    def get_current_user(self):
        return self.get_secure_cookie("mysky_user")


class Main(BaseHandler):
    @gen.coroutine
    def get(self):
        files_list = yield database.get_files_list()
        logging.debug(f'{files_list}')
        self.render('main.html',
                    title='Полка pdf',
                    files_list=files_list,
                    error_message='',
                    current_user=self.current_user, )


class Preview(BaseHandler):
    async def get(self, hashed_name):
        # print(f'{hashed_name}')
        self.redirect('/')


class PostFile(BaseHandler):
    SUPPORTED_METHODS = ('POST', )

    def initialize(self):
        self.io_loop = IOLoop.current()

    # @web.authenticated
    async def post(self, *args, **kwargs):
        # logging.debug(f'{dir(self)}')
        for field_name, files in self.request.files.items():
            # logging.info(f'POST {field_name} {files}')
            for info in files:
                filename, content_type = info['filename'], info['content_type']
                body = info['body']
                logging.info(f'POSTed {field_name} «{filename}» {content_type} {len(body)} bytes')
                if content_type.lower() in settings.CONTENT_TYPES:
                    pdf_file = updf.PDF(pdf_name=filename, user_name=self.current_user)
                    self.io_loop.add_future(pdf_file.save(body),
                                            self.save_pdf_completed)
        self.redirect('/')

    def save_pdf_completed(self, future):
        pdf_name, hashed_name, user_name = future.result()
        logging.info(f'{pdf_name}, {hashed_name}, {user_name}')


class REST(BaseHandler):
    SUPPORTED_METHODS = ('delete',)
    async def delete(self):
        pass


class Login(BaseHandler):
    async def get(self):
        try:
            error_message = self.get_argument('error')
        except Exception as e:
            error_message = ''
        self.render('main.html', title='Введите логин и пароль',
                    error_message=error_message
                    # options={'users': await database.get_users()}
                    )

    async def check_permission(self, user_name, user_password):
        auth_user = await database.auth_user(user_name, user_password)
        return True

    def set_current_user(self, user_name):
        if user_name:
            self.set_secure_cookie("mysky_user", user_name.encode())
        else:
            self.clear_cookie("mysky_user")

    async def post(self):
        user_name = self.get_argument('user_name')
        user_password = self.get_argument('password')
        auth_user = await self.check_permission(user_name, user_password)
        if auth_user:
            self.set_current_user(user_name)
            # self.current_user = user_name
            error_message = ''
        else:
            error_message = 'Не подходит'
        self.redirect('/')


class Logout(BaseHandler):
    # @web.authenticated
    async def get(self):
        self.clear_cookie("mysky_user")
        self.redirect('/')
