# modules/file_handler.py
import os
from pathlib import Path
from io import BytesIO

def get_file_extension(uploaded_file):
    return uploaded_file.name.split(".")[-1].lower()

def load_file_content(uploaded_file):
    content = uploaded_file.read()
    ext = get_file_extension(uploaded_file)
    return content, ext

def save_file(content_bytes: bytes, file_name: str):
    return BytesIO(content_bytes)
