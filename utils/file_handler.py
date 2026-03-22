import os
import hashlib
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader,TextLoader

def get_file_md5_hex(file_path:str):
    #如果文件不存在，返回None
    if not os.path.exists(file_path):
        logger.error(f"文件不存在:{file_path}")
        return
    #判断是否文件
    if not os.path.isfile(file_path):
        logger.error(f"不是文件:{file_path}")
        return
    md5_obj = hashlib.md5()
    chunk_size=4096
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                md5_obj.update(chunk)
            md5_hex=md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        logger.error(f"获取文件MD5失败:{file_path},{str(e)}")
        return

#获取指定目录下的所有文件
def listdir_with_allowed_type(path:str,allowed_types:tuple[str]):
    files=[]
    if not os.path.isdir(path):
        logger.error(f"路径不存在:{path}")
        return allowed_types
    for f in os.listdir(path):
        if f.endswith(allowed_types):
            files.append(os.path.join(path,f))
    return tuple(files)

def pdf_loader(file_path:str,passwd:str=None)->list[Document]:
    return PyPDFLoader(file_path,passwd).load()

def txt_loader(file_path:str)->list[Document]:
    return TextLoader(file_path,encoding="utf-8").load()
