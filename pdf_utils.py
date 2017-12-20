#!/usr/bin/python3
import os
import hashlib
import time
# from PythonMagick import Image
import settings


async def save_png_page(page_no: int, pdf_fd=None):
    hashed_name = hashlib.md5(f'{time.time()}'.encode()).hexdigest()
    hashed_name = os.path.join(settings.MEDIA_PAGES, f'{hashed_name}.png')
    # TODO: Записать в папку
    # pdf_fd = pdf_fd if pdf_fd else
    # Image
    return hashed_name, pdf_fd
