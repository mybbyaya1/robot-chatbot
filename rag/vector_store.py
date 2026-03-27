from langchain_chroma import Chroma
from langchain_core.documents import Document

from utils.config_handler import chroma_conf
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex,ppt_loader,excel_loader,word_loader
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


class VectorStoreService:
    def __init__(self):
        self.vector_store=Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=chroma_conf["persist_directory"],
        )
        self.spliter=RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )
        # 初始化时自动加载文档
        self.load_document()
    def get_retriever(self):
        return self.vector_store.as_retriever(search_kargs={"k":chroma_conf["k"]})
    def load_document(self):
        '''
        从数据库文件夹内读取数据文件，转为向量存入向量库
        要计算文件的md5去重
        :return:
        '''
        def check_md5_hex(md5_for_check:str):
            # 如果不存在md5文件，则创建文件后关闭
            if not os.path.exists(get_abs_path(chroma_conf["md5_hex_store"])):
                open(get_abs_path(chroma_conf["md5_hex_store"]), "w", encoding="utf-8").close()
                return False
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "r", encoding="utf-8") as f:
                md5_hex_list=f.readlines()
                for md5_hex in md5_hex_list:
                    if md5_hex.strip()==md5_for_check:
                        #md5处理过
                        return True
                return False

        def save_md5_hex(md5_for_save: str):
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_save+"\n")

        #导入文件，获取document
        def get_file_documents(read_path:str):
            if read_path.endswith(".pdf"):
                return pdf_loader(read_path)
            elif read_path.endswith(".txt"):
                return txt_loader(read_path)
            elif read_path.endswith(".pptx"):
                return ppt_loader(read_path)
            elif read_path.endswith(".xls"):
                return excel_loader(read_path)
            elif read_path.endswith(".docx"):
                return word_loader(read_path)
            else:
                return []

        allowed_files_path:list[str]=listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"]),
        )
        for path in allowed_files_path:
            md5_hex=get_file_md5_hex(path)
            if check_md5_hex(md5_hex):
                logger.info(f"文件已处理过:{path}")
                continue

            try:
                documents:list[Document]=get_file_documents(path)
                if not documents:
                    logger.info(f"[加载知识库]文件内容为空:{path}.跳过")
                    continue
                split_documents:list[Document]=self.spliter.split_documents(documents)
                if not split_documents:
                    logger.info(f"[加载知识库]文件内容已切分空:{path}.跳过")
                    continue
                self.vector_store.add_documents(split_documents)
                #记录这个已经处理过了
                save_md5_hex(md5_hex)
                logger.info(f"[加载知识库]成功:{path}")
            except Exception as e:
                logger.error(f"[加载知识库]失败:{path},{str(e)}")
                continue

if __name__ == '__main__':
    service=VectorStoreService()
    service.load_document()
    retriever=service.get_retriever()
    res=retriever.invoke("迷路")
    for r in res:
        print(r.page_content)
        print("*"*20)




















