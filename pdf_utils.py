#!/usr/bin/python3
import hashlib
import time
from PyPDF2 import PdfFileReader
from tornado.log import logging
from tornado.gen import coroutine
# from wand.image import Image
# from wand.color import Color
from pgmagick import Image, Color
import settings
import database


class PNGPage(object):
    def __init__(self, pdf_id: int, page_no: int, page_id: int=None, hashed_name: str=None):
        self._page_id = page_id
        self._pdf_id = pdf_id
        self._hashed_name = hashed_name
        self._page_no = page_no

    @property
    def hashed_name(self):
        return self._hashed_name

    @property
    def page_id(self):
        return self._page_id

    @coroutine
    def generate(self):
        if not self._hashed_name:
            self._hashed_name = hashlib.md5(f'{time.time()}'.encode()).hexdigest()
            page = Image(f'{settings.MEDIA_PAGES}/{self._hashed_name}.pdf[{self._page_no}]')
            # page.format = settings.PREVIEW_FORMAT
            # page.background_color = Color(settings.PREVIEW_BACKGROUND_COLOR)
            # page.alpha_channel = 'remove'
            page.write(f'{settings.MEDIA_PAGES}/{self._hashed_name}.{settings.PREVIEW_FORMAT}')
            self._page_id = yield database.insert_page(self._pdf_id, self._hashed_name)
        return self._hashed_name


class PDF(object):
    def __init__(self, pdf_name: str, user_name: str, pdf_id: int=0, user_id: int=0, hashed_name: str=None):
        self._pdf_id = pdf_id
        self._user_name = user_name
        self._user_id = user_id  # Владелец user_id
        self._name = pdf_name
        self._hashed_name = ''
        self._pages = {}  # {(page_no:int): page:PNGPage, }
        self._total_pages = None
        self._pdf_file = None  # Wand object

    def __del__(self):
        if self._pdf_file:
            self._pdf_file.close()

    @coroutine
    def save(self, body):
        if not self._pdf_id:
            self._hashed_name = yield self.hashed_name()
            with open(f'{settings.MEDIA_PDF}/{self._hashed_name}.pdf', 'wb') as pdf:
                pdf.write(body)
            logging.info(f'PDF.save: {self._name} -> {self._hashed_name} saved')
            self._total_pages = PdfFileReader(
                f'{settings.MEDIA_PDF}/{self._hashed_name}.pdf').getNumPages()
            self._pdf_id, *_ = yield database.insert_pdf(self._name,
                                                         self._hashed_name,
                                                         self._user_name,
                                                         self._total_pages)
            logging.info(
                f'PDF.save: {self._pdf_id} {self._total_pages} {self._hashed_name}.pdf')
        return self._name, self._hashed_name, self._user_name

    @coroutine
    def hashed_name(self):
        if self._pdf_id:
            self._hashed_name = yield database.get_pdf_hashed_name(self._pdf_id)
        else:
            self._hashed_name = hashlib.md5(f'{time.time()}'.encode()).hexdigest()
        return self._hashed_name

    @property
    def total_pages(self):
        return len([p[0] for p in enumerate(self._pdf_file.sequence)])

    @coroutine
    def pages(self, pages_list: tuple=tuple(), is_range: bool=False):
        return_pages = tuple()
        if self._pdf_id:
            if pages_list:
                pages_list = sorted(pages_list)
                if not is_range and (len(pages_list) != 2):  # Список страниц
                    pass
                elif len(pages_list) == 2:  # Диапазон страниц
                    if pages_list[0] != pages_list[1]:
                        pages_list = range(pages_list[0], pages_list[1])
                    else:
                        pages_list = (pages_list[0], )

                for p in pages_list:
                    if p < self._total_pages:
                        return_pages += ((p, self.page[p]), )
                    else:
                        break
            else:
                # Загрузим уже имеющиеся
                for p in (yield database.get_pdf_pages(self._pdf_id)):
                    self._pages.update({p: PNGPage(pdf_file=self._pdf_file,
                                                   page_no=p['page'],
                                                   page_id=p['id'],
                                                   hashed_name=p['hashed_name'])})
                    return_pages += ((p, self._pages[p]), )
        return return_pages

    @property
    def page(self, page_no: int):
        if (page_no < self._total_pages) and (page_no > -1):
            if page_no not in self._pages.keys():
                self._pages.update({page_no: PNGPage(page_no=page_no)})
            if not self._pages[page_no].hashed_name:
                yield self._pages[page_no].generate()
            return self._pages[page_no]


