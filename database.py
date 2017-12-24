#!/usr/bin/python3
import datetime
import sqlite3
import hashlib
import concurrent.futures
from tornado.gen import coroutine
from tornado.locks import BoundedSemaphore
from tornado.log import logging
import settings


executor = concurrent.futures.ProcessPoolExecutor(settings.MAX_POOL_EXECUTORS)
sqlite_semaphore = BoundedSemaphore()
db = sqlite3.connect(f'{settings.DB_PATH}',)
db.row_factory = lambda _cursor, row: {col[0]: row[i] for i, col in enumerate(_cursor.description)}
cursor = db.cursor()


def _row_factory(_cursor, row):
    return {col[0]: row[i] for i, col in enumerate(_cursor.description)}


@coroutine
def _get_sql(sql_name: str):
    sql_name = sql_name.lower()
    sql_name += '.sql' if not sql_name.endswith('.sql') else sql_name
    try:
        with open(f'{settings.SQL_PATH}/{sql_name}', 'r') as sqlf:
            sql_text = (' '.join(sqlf.readlines()))
    except Exception as e:
        logging.error(f'{e}')
        sql_text = None
    return sql_text


@coroutine
def _execute(sql_name: str, ARGS: tuple):
    SQL = yield _get_sql(sql_name)
    # logging.debug(f'_execute: {SQL}')
    data = None
    if SQL:
        with (yield sqlite_semaphore.acquire()):  # был бы потокобезопасным...
            # logging.debug(f'{db.row_factory}')
            try:
                # logging.info(f'_execute: {SQL} {ARGS}')
                cursor.execute(SQL, ARGS)
                SQL = SQL.upper()
                if SQL.startswith('INSERT '):
                    db.commit()
                    data = cursor.lastrowid
                else:
                    data = cursor.fetchall()
                logging.info(f'_execute: {data}')
            except Exception as e:
                logging.error(f'{e}')
                logging.info(f'_execute: {SQL} {ARGS}')
    return data


async def auth_user(name: str, password: str):
    password = hashlib.sha256(f'{password}'.encode()).hexdigest()
    user = await _execute('select_user_auth',
                          ({'name': name, 'password': password}, ))
    logging.info(f'database.auth_user: {user}')
    return user


@coroutine
def insert_pdf(pdf_name: str, hashed_name: str, user_name: str, total_pages: int=-1):
    user_id = yield _execute('select_user_id', {'user_name': user_name}, )
    logging.info(f'insert_pdf: user_name={user_name} user_id={user_id} selected')
    user_id = user_id[0]['id'] if user_id is not None else 0
    # logging.info(f'insert_pdf: user_name={user_name} user_id={user_id} selected')
    pdf_id = yield _execute('insert_pdf_file',
                            {'name': pdf_name,
                             'hashed_name': hashed_name,
                             'loaded': datetime.datetime.now(),
                             'pages': total_pages,
                             'user_id': user_id},)
    logging.debug(f'insert_pdf: {pdf_id} {pdf_name} {user_id} inserted')
    return pdf_id, pdf_name, user_id, hashed_name  #, pages


@coroutine
def get_files_list(current_user: str=None):
    # logging.info('database.get_files_list')
    pdf_files = yield _execute('select_pdf_files', {})
    logging.debug(f'database.get_files_list {pdf_files}')
    return pdf_files


@coroutine
def get_pdf_hashed_name(pdf_id: int):
    hashed_name = yield _execute('select_pdf_hashed_name', {'pdf_id': pdf_id})
    return hashed_name


@coroutine
def get_real_file_name(hashed_name: str):
    return_file_name = yield _execute('select_real_file_name', {'name': hashed_name})
    return return_file_name


@coroutine
def get_pdf_by_hashed_name(hashed_name: str):
    pdf_file = yield _execute('select_pdf_by_hashed_name', {'hashed_name': hashed_name})
    return pdf_file


def init():
    SQL = (("CREATE TABLE if not exists pdf_files (id INTEGER PRIMARY KEY ON CONFLICT ROLLBACK "
            "AUTOINCREMENT "
            "UNIQUE ON CONFLICT ROLLBACK "
            "NOT NULL ON CONFLICT ROLLBACK, "
            "name STRING NOT NULL ON CONFLICT ROLLBACK, "
            "hashed_name STRING (32) UNIQUE ON CONFLICT ROLLBACK "
            "NOT NULL ON CONFLICT ROLLBACK, "
            "loaded DATETIME NOT NULL ON CONFLICT ROLLBACK DEFAULT (datetime('now', 'localtime')), "
            "published DATETIME, "
            "user_id INTEGER NOT NULL ON CONFLICT ROLLBACK, "
            "pages INTEGER)"),
           ('CREATE TABLE if not exists users ('
            'id INTEGER PRIMARY KEY ON CONFLICT ROLLBACK AUTOINCREMENT UNIQUE ON CONFLICT ROLLBACK NOT NULL ON CONFLICT ROLLBACK, '
            'name STRING UNIQUE ON CONFLICT ROLLBACK NOT NULL ON CONFLICT ROLLBACK, '
            'password STRING (64) NOT NULL ON CONFLICT ROLLBACK);'),
           ('INSERT INTO users (name, password) '
            'values ("user", "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8");'),)
    for sql in SQL:
        try:
            c = db.cursor()
            c.execute(sql)
            c.close()
            db.commit()
        except Exception as e:
            # print(e)
            pass
