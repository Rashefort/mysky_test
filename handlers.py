#!/usr/bin/python3
import os
from tornado.log import logging
from tornado import web
from tornado import gen
import pdf_utils as updf
import database
import settings


class BaseHandler(web.RequestHandler):

    async def data_received(self):
        logging.debug(f'{self.request}')

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
                    current_user=self.current_user.decode(), )


class Preview(BaseHandler):
    @gen.coroutine
    def get(self, **params):
        hashed_name = params['hashed_name']
        page = int(params['page']) if params['page'] else 1

        pdf_name, png_url, page, pages = yield updf.get_page_url(hashed_name, page-1)
        # pdf_name, pages = yield updf.pdf_file_pages(hashed_name)
        prev_page, next_page = page-1, page+1
        prev_page = (updf.page_url(prev_page, hashed_name)) if prev_page > 0 else None
        next_page = (updf.page_url(next_page, hashed_name)) if next_page < pages else None
        png_url_download = pdf_name.replace('.pdf', f'-page_{page}.png')

        self.render('preview_page.html',
                    png_url=png_url,
                    hashed_name=hashed_name,
                    title=f'{page} стр. {pdf_name}',
                    pdf_name=pdf_name,
                    png_url_download=png_url_download,
                    page=page,
                    pages=pages,
                    prev_page=prev_page,
                    next_page=next_page)

    @gen.coroutine
    def post(self, **params):
        hashed_name = params['hashed_name']
        page = self.get_argument('page_num')
        self.redirect(f'/pdf/{hashed_name}/{page}')


# @web.stream_request_body - не умеет передавать имя файла... :(
class PostFile(BaseHandler):
    SUPPORTED_METHODS = ('POST', )

    @gen.coroutine
    def post(self, *args, **kwargs):
        # logging.debug(f'{dir(self)}')
        for field_name, files in self.request.files.items():
            # logging.info(f'POST {field_name} {files}')
            for info in files:
                filename, content_type = info['filename'], info['content_type']
                body = info['body']
                logging.info(f'POSTed {field_name} «{filename}» {content_type} {len(body)} bytes')
                if content_type.lower() in settings.CONTENT_TYPES:
                    pdf_file = yield updf.save_pdf_file(body, filename, self.current_user.decode())
        self.redirect('/')


# class REST(BaseHandler):
#     SUPPORTED_METHODS = ('delete',)
#     async def delete(self):
#         pass


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

    async def set_current_user(self, user_name):
        if user_name:
            self.set_secure_cookie("mysky_user", user_name.encode())
        else:
            self.clear_cookie("mysky_user")

    async def post(self):
        user_name = self.get_argument('user_name')
        user_password = self.get_argument('password')
        auth_user = await self.check_permission(user_name, user_password)
        if auth_user:
            await self.set_current_user(user_name)
            # self.current_user = user_name
            error_message = ''
        else:
            error_message = 'Не подходит'
        self.redirect('/')


class Logout(BaseHandler):

    async def get(self):
        self.clear_cookie("mysky_user")
        self.redirect('/')


class PdfFileStreamDownload(BaseHandler):
    def initialize(self, file_path):
        self.file_path = file_path

    @web.asynchronous
    @gen.engine
    def get(self, hashed_name):
        file_size = os.path.getsize(f'{self.file_path}/{hashed_name}.pdf')
        logging.info(f'download handler: {self.file_path}/{hashed_name} {file_size} bytes')
        self.set_header('Content-Type', 'application/pdf')
        self.set_header('Content-length', file_size)
        self.flush()
        fd = open(f'{self.file_path}/{hashed_name}.pdf', 'rb')
        complete_download = False
        while not complete_download:
            data = fd.read(settings.CHUNK_SIZE)
            logging.info(f'download chunk: {len(data)} bytes')
            if len(data) > 0:
                self.write(data)
                yield gen.Task(self.flush)
            complete_download = (len(data) == 0)
        fd.close()
        self.finish()


class PngFileStreamDownload(BaseHandler):
    def initialize(self, file_path):
        self.file_path = file_path

    @web.asynchronous
    @gen.engine
    def get(self, file_name):
        file_size = os.path.getsize(f'{self.file_path}/{hashed_name}')
        logging.info(f'download handler: {self.file_path}/{hashed_name} {file_size} bytes')
        self.set_header('Content-Type', 'application/png')
        self.set_header('Content-length', file_size)
        self.flush()
        fd = open(f'{self.file_path}/{hashed_name}{page}.png', 'rb')
        complete_download = False
        while not complete_download:
            data = fd.read(settings.CHUNK_SIZE)
            logging.info(f'download chunk: {len(data)} bytes')
            if len(data) > 0:
                self.write(data)
                yield gen.Task(self.flush)
            complete_download = (len(data) == 0)
        fd.close()
        self.finish()
