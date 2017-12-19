#!/usr/bin/python3
import json
import datetime
import tornado.log
from tornado import web
import dicttoxml
from tornado.httpclient import AsyncHTTPClient
# import tornado.websocket
# from tornado.concurrent import run_on_executor
# import concurrent.futures
# from tornado import gen
# from tornado.queues import Queue
# from tornado.escape import json_encode
# from tornado.escape import json_decode
import settings
from settings import logger


class BaseHandler(web.RequestHandler):
    current_user = ''

    def get_current_user(self):
        return self.get_secure_cookie("mysky_user")


class Login(BaseHandler):
    async get(self):
        self.render('login.html', title='Введите логин и пароль',
                    options={'users': await database.get_users()})

    async def post(self):
        user_name = self.get_argument('user_name')
        user_password = self.get_argument('password')
        if (await database.auth_user(user_name, user_password)):
            self.set_secure_cookie("mysky_user", user_name.encode())
            self.current_user = user_name
            self.redirect('/login')
        else:
            self.redirect('/')


class Logout(BaseHandler):
    @web.authenticated
    async get(self):
        self.clear_session_cookies("mysky_user")
        self.redirect('/login')

