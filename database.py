#!/usr/bin/python3
import datetime
import json
import sqlite3
import hashlib
import PyPDF2 as PDF
import PythonMagick as magic
from tornado.locks import BoundedSemaphore
import models
import settings
from settings import logger


sqlite_semaphore = BoundedSemaphore()
db = sqlite3.connect(f'sqlite:///{settings.DB_PATH}',)
cursor = db.cursor()


def _row_factory(cursor, row):
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}


async def _get_sql(sql_name: str):
    sql_name = sql_name.lower()
    sql_name += '.sql' if not sql_name.endswith('.sql') else sql_name
    try:
        with open(f'{settings.SQL_PATH}/{sql_name}', 'r') as f:
            return ' '.join(f.readlines())
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
                logger.error(f'{f}')
    return data


async def auth_user(name: str, password: str):
    user = await _execute('select_user_auth',
                          ({'name': name, 'password': name}, ))
    logger.info(f'database.auth_user: {user})
    return user


async def insert_pdf_row(name: str, loaded: datetime.datetime, user_id: int):
    hased_name = hashlib.md5(f'{name}{time.time()}'.encode()).hexdigest()
    await _execute('insert_pdf_file', ({'name': name,
                                        'hashed_name': hashed_name,
                                        'loaded': loaded,
                                        'user_id': user_id}, ))


async def generate_page(page_name: str, ):
    pass


async def generate_pages(pdf_id: int, pdf_name: str):
    pdf_im = PDF.PdfFileReader(file)
    await generate_page()


async def insert_page(pdf_id: int, hashed_name: str):
    page_id = await _execute('insert_pdf_page', ({'hashed_name': hashed_name, 'pdf_id': pdf_id}, ))
    return page_id


async def insert_pages(pdf_id: int, pdf_name: str):

    await insert_page(pdf_id, hashed_name)


async def get_pdf_pages(pdf_id: int):
    pages = await _execute('select_pdf_pages', ({'pdf_id': pdf_id}, ))
    return pages


