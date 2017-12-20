#!/usr/bin/python3
import datetime
import time
import json
import sqlite3
import hashlib
import PyPDF2 as PDF
# import PythonMagick as magic
from tornado.locks import BoundedSemaphore
# from tornado.concurrent import return_future
import settings
from settings import logger
import pdf_utils as updf


sqlite_semaphore = BoundedSemaphore()
db = sqlite3.connect(f'sqlite:///{settings.DB_PATH}',)
cursor = db.cursor()


def _row_factory(_cursor, row):
    return {col[0]: row[i] for i, col in enumerate(_cursor.description)}


async def _get_sql(sql_name: str):
    sql_name = sql_name.lower()
    sql_name += '.sql' if not sql_name.endswith('.sql') else sql_name
    try:
        with open(f'{settings.SQL_PATH}/{sql_name}', 'r') as sqlf:
            return ' '.join(sqlf.readlines())
    except Exception as e:
        logger.error(f'{e}')
        return None


async def _execute(sql_name: str, ARGS: tuple):
    SQL = await _get_sql(sql_name)
    data = None
    if SQL:
        async with sqlite_semaphore:
            try:
                cursor.executemany(SQL, ARGS)
                SQL = SQL.upper()
                if SQL.startswith('INSERT ') or SQL.startswith('UPDATE '):
                    db.commit()
                    data = cursor.lastrow_id
                else:
                    data = cursor.fetchmany()
            except Exception as e:
                logger.error(f'{e}')
    return data


async def auth_user(name: str, password: str):
    password = hashlib.sha256(f'{password}'.encode()).hexdigest()
    user = await _execute('select_user_auth',
                          ({'name': name, 'password': password}, ))
    logger.debug(f'database.auth_user: {user}')
    return user


async def insert_page(pdf_id: int, hashed_name: str):
    page_id = await _execute('insert_pdf_page', ({'hashed_name': hashed_name,
                                                  'pdf_id': pdf_id}, ))
    return page_id


async def generate_pages(pdf_id: int, hashed_name: str):
    # pdf_file = await _execute('select_pdf_file', ({'pdf_id': pdf_id},))
    pdf_pages = PDF.PdfFileReader(f'{settings.MEDIA_PDF}/{hashed_name}.pdf').getNumPages()
    pdf_fd = None  # Чтобы каждый раз pdf не открывать...
    pages = set()
    for page in range(pdf_pages-1):
        png_hashed_name, pdf_fd = await updf.save_png_page(page, pdf_fd)
        logger.debug(f'page {page} {png_hashed_name} generated')
        page_id = await insert_page(pdf_id, png_hashed_name)
        logger.debug(f'page {page} {png_hashed_name} {page_id} inserted')
        pdf_pages.add(page_id)
    return pages


async def save_pdf_completed(pdf_name: str, hashed_name: str, user_id: int):
    pdf_id = await _execute('insert_pdf_file',
                            ({'name': pdf_name,
                              'hashed_name': hashed_name,
                              'loaded': datetime.datetime.now(),
                              'user_id': user_id},))
    logger.debug(f'save_pdf_completed: {pdf_id} {pdf_name} {user_id} inserted')
    pages = await generate_pages(pdf_id, hashed_name)
    logger.debug(f'save_pdf_completed: {pdf_name} {pages} generated')
    await _execute('update_pdf_pages',
                   ({'pages': len(pages), 'pdf_id': pdf_id}, ))
    return pdf_id


async def save_pdf(pdf_name: str, pdf_body: bytes, user_name: str):
    user_id = await _execute('select_user_id', ({'name': user_name}, ))
    hashed_name = hashlib.md5(f'{pdf_name}{time.time()}'.decode()).hexdigest()

    # Сохранить pdf
    with open(f'{settings.MEDIA_PDF}/{hashed_name}.pdf', 'wb') as pdf:
        pdf.write_bytes(pdf_body)

    return pdf_name, hashed_name, user_id


async def get_files_list(current_user: str):
    pages = await _execute('select_pdf_files', {})
    return pages
