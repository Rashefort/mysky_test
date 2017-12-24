#!/usr/bin/python3
import hashlib
import time
import os
from PyPDF2 import PdfFileReader
from tornado.log import logging
from tornado.gen import coroutine
from pgmagick import Image
import settings
import database


def page_url(page: int, hashed_name: str):
    return f'/pdf/{hashed_name}/{page}', page


@coroutine
def pdf_file_pages(hashed_name: str):
    pdf_file = yield database.get_pdf_by_hashed_name(hashed_name)
    pdf_file = pdf_file[0] if pdf_file else None
    if pdf_file:
        pdf_name = pdf_file['name']
        pdf_pages = pdf_file['pages']
    else:
        pdf_name, pdf_pages = None, None
    return pdf_name, pdf_pages


@coroutine
def get_page_url(hashed_name: str, page: int):
    pdf_name, max_pages = yield pdf_file_pages(hashed_name)
    page = min(page, max_pages-1)
    page = max(0, page)
    pdf_file = f'{settings.MEDIA_PDF}/{hashed_name}.pdf[{page}]'
    png_file = f'{hashed_name}{page}.{settings.PREVIEW_FORMAT}'
    if not os.path.exists(f'{settings.MEDIA_PAGES}/{png_file}'):
        pdf = Image(pdf_file)
        pdf.write(f'{settings.MEDIA_PAGES}/{png_file}')
        logging.debug(f'get_png_url: generated {page} page {png_file}')
    png_url = f'/pages/{png_file}'
    return pdf_name, png_url, page+1, max_pages


@coroutine
def save_pdf_file(body: bytes, pdf_name: str, user_name: str):
    hashed_name = hashlib.md5(f'{time.time()}'.encode()).hexdigest()
    with open(f'{settings.MEDIA_PDF}/{hashed_name}.pdf', 'wb') as pdf:
        pdf.write(body)
    total_pages = PdfFileReader(f'{settings.MEDIA_PDF}/{hashed_name}.pdf').getNumPages()
    pdf_data = yield database.insert_pdf(pdf_name, hashed_name, user_name, total_pages)
    logging.debug(f'save_pdf_file: {pdf_name} ({total_pages} pages) saved ({len(body)} bytes) in {hashed_name}.pdf')
    return pdf_data

